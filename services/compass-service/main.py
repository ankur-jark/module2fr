"""Compass Microservice - Career Discovery Module"""
from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime
import json

# Add parent directory to path for shared imports
sys.path.append(str(Path(__file__).parent.parent))
from shared.utils import ServiceRegistry, EventPublisher, get_redis_client, get_openai_client
from shared.schemas import ProfileComponent, ServiceEvent

# Import Compass specific components
from compass_schemas import (
    JourneyInitRequest,
    JourneyState,
    GeneratedQuestion,
    JourneyDecision,
    CompletedProfile,
    ConfidenceScore
)
from compass_orchestrator import CompassOrchestrator

load_dotenv()

# Global instances
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    redis_client = await get_redis_client()
    openai_client = get_openai_client()
    
    app_state["redis"] = redis_client
    app_state["openai"] = openai_client
    app_state["service_registry"] = ServiceRegistry(redis_client)
    app_state["event_publisher"] = EventPublisher(redis_client)
    app_state["orchestrator"] = CompassOrchestrator(
        openai_client=openai_client,
        redis_client=redis_client,
        event_publisher=app_state["event_publisher"]
    )
    
    # Register this service
    await app_state["service_registry"].register_service(
        "compass-service",
        os.getenv("COMPASS_HOST", "localhost"),
        int(os.getenv("COMPASS_PORT", "8001")),
        "/health"
    )
    
    yield
    
    # Shutdown
    await app_state["service_registry"].deregister_service("compass-service")
    await redis_client.close()

app = FastAPI(
    title="Compass Service",
    description="AI-powered career discovery microservice",
    version="1.0.0",
    lifespan=lifespan
)

# Dependencies
def get_orchestrator() -> CompassOrchestrator:
    return app_state["orchestrator"]

def get_event_publisher() -> EventPublisher:
    return app_state["event_publisher"]

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "compass-service",
        "version": "1.0.0",
        "capabilities": ["motivators", "interests"]
    }

# Journey Management
@app.post("/journey/start")
async def start_journey(
    request: JourneyInitRequest,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator),
    publisher: EventPublisher = Depends(get_event_publisher)
):
    """Start a new Compass journey"""
    try:
        journey_state = await orchestrator.start_journey(request)
        
        # Publish event for other services
        await publisher.publish("compass.journey.started", {
            "event_type": "journey_started",
            "service_origin": "compass-service",
            "user_id": request.user_id,
            "journey_id": journey_state.journey_id,
            "data": {
                "demographics": request.demographics.model_dump(),
                "preferences": request.preferences.model_dump()
            }
        })
        
        return journey_state.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/journey/{journey_id}")
async def get_journey(
    journey_id: str,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator)
):
    """Get current journey state"""
    journey_state = await orchestrator.get_journey_state(journey_id)
    if not journey_state:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey_state.model_dump()

@app.post("/journey/{journey_id}/next-question")
async def get_next_question(
    journey_id: str,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator)
):
    """Generate next question"""
    try:
        question = await orchestrator.generate_next_question(journey_id)
        # Sanitize response to remove any RAISEC-related content
        payload = question.model_dump()
        # Remove riasec_weights from options if present
        if "options" in payload and isinstance(payload["options"], list):
            for opt in payload["options"]:
                if isinstance(opt, dict):
                    opt.pop("riasec_weights", None)
        # Remove any mention of 'riasec' in target dimensions if present
        td = payload.get("target_dimensions")
        if isinstance(td, dict):
            if isinstance(td.get("secondary_dimensions"), list):
                td["secondary_dimensions"] = [d for d in td["secondary_dimensions"] if d.lower() != "riasec"]
            if isinstance(td.get("primary_dimension"), str) and td["primary_dimension"].lower() == "riasec":
                td["primary_dimension"] = "interests_motivators"
        return payload
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

class ResponseSubmission(BaseModel):
    question_id: str
    response_text: str
    response_time_seconds: Optional[int] = None
    skipped: bool = False

class ProfileUpdateRequest(BaseModel):
    current_confidence: Optional[ConfidenceScore] = None
    reason: Optional[str] = None  # Why the user is updating

@app.post("/journey/{journey_id}/respond")
async def submit_response(
    journey_id: str,
    response_data: ResponseSubmission,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator),
    publisher: EventPublisher = Depends(get_event_publisher)
):
    """Submit response to a question"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Processing response for journey {journey_id}, question {response_data.question_id}")
        
        decision = await orchestrator.process_response(
            journey_id=journey_id,
            question_id=response_data.question_id,
            response_text=response_data.response_text,
            response_time_seconds=response_data.response_time_seconds,
            skipped=response_data.skipped
        )
        
        # If journey completed, publish profile component
        if decision.decision == "complete":
            journey_state = await orchestrator.get_journey_state(journey_id)
            if journey_state.completed_profile:
                await _publish_profile_component(
                    journey_state.completed_profile,
                    publisher
                )
        
        return decision.model_dump()
    except ValueError as e:
        logger.error(f"ValueError in submit_response: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in submit_response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/journey/{journey_id}/complete")
async def complete_journey(
    journey_id: str,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator),
    publisher: EventPublisher = Depends(get_event_publisher)
):
    """Complete journey and get profile"""
    try:
        profile = await orchestrator.complete_journey(journey_id)
        
        # Publish profile component for aggregation
        await _publish_profile_component(profile, publisher)
        
        return profile.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/profile/{journey_id}")
async def get_profile(
    journey_id: str,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator)
):
    """Get completed profile"""
    journey_state = await orchestrator.get_journey_state(journey_id)
    if not journey_state:
        raise HTTPException(status_code=404, detail="Journey not found")
    
    if not journey_state.completed_profile:
        raise HTTPException(status_code=400, detail="Journey not completed")
    
    return journey_state.completed_profile.model_dump()

@app.post("/journey/{journey_id}/update-profile")
async def update_journey_profile(
    journey_id: str,
    update_data: ProfileUpdateRequest,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator),
    publisher: EventPublisher = Depends(get_event_publisher)
):
    """Update journey profile and confidence values"""
    try:
        # Load current journey state
        journey_state = await orchestrator.get_journey_state(journey_id)
        if not journey_state:
            raise HTTPException(status_code=404, detail="Journey not found")
        
        # Update confidence if provided
        if update_data.current_confidence:
            journey_state.current_confidence = update_data.current_confidence
        
        # Update timestamp
        journey_state.last_updated = datetime.utcnow()
        
        # Save updated state
        await orchestrator._save_journey_state(journey_state)
        
        # Publish update event
        await publisher.publish("compass.profile.updated", {
            "event_type": "profile_updated",
            "service_origin": "compass-service",
            "user_id": journey_state.user_id,
            "journey_id": journey_id,
            "reason": update_data.reason,
            "updated_fields": {
                "confidence_updated": update_data.current_confidence is not None
            }
        })
        
        return {
            "status": "success",
            "message": "Profile updated successfully",
            "journey_id": journey_id,
            "updated_at": journey_state.last_updated
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to publish profile component
async def _publish_profile_component(
    profile: CompletedProfile,
    publisher: EventPublisher
):
    """Publish profile as a component for aggregation"""
    component = ProfileComponent(
        component_type="compass_profile",
        service_origin="compass-service",
        confidence=profile.confidence_at_completion,
        data={
            "motivators": profile.motivators,
            "interests": profile.interests,
            "insights": profile.insights.model_dump()
        },
        generated_at=profile.completion_date if profile.completion_date else datetime.utcnow(),
        version="1.0"
    )
    
    # Convert component to dict with JSON-safe datetime handling
    component_dict = component.model_dump()
    if 'generated_at' in component_dict and isinstance(component_dict['generated_at'], datetime):
        component_dict['generated_at'] = component_dict['generated_at'].isoformat()
    
    await publisher.publish("profile.component.ready", {
        "event_type": "profile_component_ready",
        "service_origin": "compass-service",
        "user_id": profile.user_id,
        "component": component_dict
    })

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("COMPASS_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
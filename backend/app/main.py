from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import redis.asyncio as redis
from typing import Optional

from app.schemas.compass_schemas import (
    JourneyInitRequest,
    JourneyState,
    GeneratedQuestion,
    JourneyDecision,
    CompletedProfile
)
from app.services.compass_orchestrator import CompassOrchestrator

# Load environment variables
load_dotenv()

# Global instances
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app_state["openai_client"] = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    app_state["redis_client"] = await redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379"),
        decode_responses=True
    )
    app_state["orchestrator"] = CompassOrchestrator(
        openai_client=app_state["openai_client"],
        redis_client=app_state["redis_client"]
    )
    
    yield
    
    # Shutdown
    await app_state["redis_client"].close()

# Create FastAPI app
app = FastAPI(
    title="Compass Module API",
    description="AI-powered career discovery system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get orchestrator
def get_orchestrator() -> CompassOrchestrator:
    return app_state["orchestrator"]

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "compass-module"}

# Journey Management Endpoints

@app.post("/api/v1/journey/start", response_model=JourneyState)
async def start_journey(
    request: JourneyInitRequest,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator)
):
    """Start a new Compass journey for a user"""
    try:
        journey_state = await orchestrator.start_journey(request)
        return journey_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/journey/{journey_id}", response_model=JourneyState)
async def get_journey(
    journey_id: str,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator)
):
    """Get current state of a journey"""
    journey_state = await orchestrator.get_journey_state(journey_id)
    if not journey_state:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey_state

@app.post("/api/v1/journey/{journey_id}/next-question", response_model=GeneratedQuestion)
async def get_next_question(
    journey_id: str,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator)
):
    """Generate the next question for the journey"""
    try:
        question = await orchestrator.generate_next_question(journey_id)
        return question
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/journey/{journey_id}/respond", response_model=JourneyDecision)
async def submit_response(
    journey_id: str,
    question_id: str,
    response_text: str,
    response_time_seconds: Optional[int] = None,
    skipped: bool = False,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator)
):
    """Submit a response to a question"""
    try:
        decision = await orchestrator.process_response(
            journey_id=journey_id,
            question_id=question_id,
            response_text=response_text,
            response_time_seconds=response_time_seconds,
            skipped=skipped
        )
        return decision
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/journey/{journey_id}/complete", response_model=CompletedProfile)
async def complete_journey(
    journey_id: str,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator)
):
    """Manually complete a journey and get the final profile"""
    try:
        profile = await orchestrator.complete_journey(journey_id)
        return profile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/journey/{journey_id}/abandon")
async def abandon_journey(
    journey_id: str,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator)
):
    """Abandon a journey"""
    try:
        journey_state = await orchestrator.abandon_journey(journey_id)
        return {"message": "Journey abandoned", "journey_id": journey_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Profile Endpoints

@app.get("/api/v1/profile/{journey_id}", response_model=CompletedProfile)
async def get_profile(
    journey_id: str,
    orchestrator: CompassOrchestrator = Depends(get_orchestrator)
):
    """Get completed profile for a journey"""
    journey_state = await orchestrator.get_journey_state(journey_id)
    if not journey_state:
        raise HTTPException(status_code=404, detail="Journey not found")
    
    if not journey_state.completed_profile:
        raise HTTPException(status_code=400, detail="Journey not completed")
    
    return journey_state.completed_profile

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
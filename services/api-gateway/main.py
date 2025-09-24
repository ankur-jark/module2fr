"""API Gateway - Main entry point for all microservices"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import uuid
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add parent directory to path for shared imports
sys.path.append(str(Path(__file__).parent.parent))
from shared.utils import ServiceRegistry, InterServiceClient, EventPublisher, get_redis_client
from shared.schemas import ServiceRequest, ServiceResponse, AggregatedProfile, ModuleProgress

load_dotenv()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Global instances
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    redis_client = await get_redis_client()
    app_state["redis"] = redis_client
    app_state["service_registry"] = ServiceRegistry(redis_client)
    app_state["inter_service"] = InterServiceClient(app_state["service_registry"])
    app_state["event_publisher"] = EventPublisher(redis_client)
    
    # Register API Gateway itself
    await app_state["service_registry"].register_service(
        "api-gateway",
        os.getenv("GATEWAY_HOST", "localhost"),
        int(os.getenv("GATEWAY_PORT", "8000")),
        "/health"
    )
    
    yield
    
    # Shutdown
    await app_state["inter_service"].close()
    await redis_client.close()

app = FastAPI(
    title="TruScholar API Gateway",
    description="Central API gateway for all TruScholar microservices",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - Allow multiple frontend ports for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
def get_inter_service() -> InterServiceClient:
    return app_state["inter_service"]

def get_event_publisher() -> EventPublisher:
    return app_state["event_publisher"]

def get_service_registry() -> ServiceRegistry:
    return app_state["service_registry"]

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

# Service discovery endpoint
@app.get("/services")
async def list_services(registry: ServiceRegistry = Depends(get_service_registry)):
    """List all registered services"""
    services = {}
    for key in ["compass-service", "user-profile-service", "skill-analyzer-service", "expertise-analyzer-service"]:
        service = await registry.get_service(key)
        if service:
            services[key] = service
    return services

# ============== COMPASS MODULE ROUTES ==============

@app.post("/api/v1/compass/start")
@limiter.limit("10/minute")
async def start_compass_journey(
    request: Request,
    user_data: Dict[str, Any],
    inter_service: InterServiceClient = Depends(get_inter_service),
    publisher: EventPublisher = Depends(get_event_publisher)
):
    """Start a Compass journey"""
    try:
        # Call Compass service
        response = await inter_service.call_service(
            "compass-service",
            "/journey/start",
            method="POST",
            data=user_data
        )
        
        # Publish event
        await publisher.publish("module.started", {
            "module": "compass",
            "user_id": user_data.get("user_id"),
            "journey_id": response.get("journey_id")
        })
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/compass/journey/{journey_id}")
async def get_compass_journey(
    journey_id: str,
    inter_service: InterServiceClient = Depends(get_inter_service)
):
    """Get Compass journey status"""
    try:
        response = await inter_service.call_service(
            "compass-service",
            f"/journey/{journey_id}",
            method="GET"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/compass/journey/{journey_id}/next-question")
async def get_next_compass_question(
    journey_id: str,
    inter_service: InterServiceClient = Depends(get_inter_service)
):
    """Get next question for Compass journey"""
    try:
        response = await inter_service.call_service(
            "compass-service",
            f"/journey/{journey_id}/next-question",
            method="POST"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/compass/journey/{journey_id}/response")
@limiter.limit("30/minute")
async def submit_compass_response(
    request: Request,
    journey_id: str,
    response_data: Dict[str, Any],
    inter_service: InterServiceClient = Depends(get_inter_service)
):
    """Submit response to Compass question"""
    try:
        response = await inter_service.call_service(
            "compass-service",
            f"/journey/{journey_id}/respond",
            method="POST",
            data=response_data
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/compass/journey/{journey_id}/abandon")
async def abandon_compass_journey(
    journey_id: str,
    inter_service: InterServiceClient = Depends(get_inter_service)
):
    """Abandon a Compass journey"""
    try:
        response = await inter_service.call_service(
            "compass-service",
            f"/journey/{journey_id}/abandon",
            method="POST"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/compass/journey/{journey_id}/update-profile")
@limiter.limit("10/minute")
async def update_compass_profile(
    request: Request,
    journey_id: str,
    profile_data: Dict[str, Any],
    inter_service: InterServiceClient = Depends(get_inter_service),
    publisher: EventPublisher = Depends(get_event_publisher)
):
    """Update Compass journey profile"""
    try:
        response = await inter_service.call_service(
            "compass-service",
            f"/journey/{journey_id}/update-profile",
            method="POST",
            data=profile_data
        )
        
        # Publish event
        await publisher.publish("profile.updated", {
            "module": "compass",
            "user_id": profile_data.get("user_id"),
            "journey_id": journey_id,
            "updated_fields": list(profile_data.keys())
        })
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== SKILL ANALYZER ROUTES ==============

@app.post("/api/v1/skills/analyze")
@limiter.limit("10/minute")
async def analyze_skills(
    request: Request,
    skill_data: Dict[str, Any],
    inter_service: InterServiceClient = Depends(get_inter_service)
):
    """Analyze user skills"""
    try:
        response = await inter_service.call_service(
            "skill-analyzer-service",
            "/analyze",
            method="POST",
            data=skill_data
        )
        return response
    except Exception as e:
        # Service might not be implemented yet
        if "not found" in str(e).lower():
            return {"message": "Skill analyzer service coming soon", "status": "not_implemented"}
        raise HTTPException(status_code=500, detail=str(e))

# ============== EXPERTISE ANALYZER ROUTES ==============

@app.post("/api/v1/expertise/analyze")
@limiter.limit("10/minute")
async def analyze_expertise(
    request: Request,
    expertise_data: Dict[str, Any],
    inter_service: InterServiceClient = Depends(get_inter_service)
):
    """Analyze user expertise"""
    try:
        response = await inter_service.call_service(
            "expertise-analyzer-service",
            "/analyze",
            method="POST",
            data=expertise_data
        )
        return response
    except Exception as e:
        # Service might not be implemented yet
        if "not found" in str(e).lower():
            return {"message": "Expertise analyzer service coming soon", "status": "not_implemented"}
        raise HTTPException(status_code=500, detail=str(e))

# ============== USER PROFILE AGGREGATOR ==============

@app.get("/api/v1/profile/{user_id}/complete")
async def get_complete_profile(
    user_id: str,
    inter_service: InterServiceClient = Depends(get_inter_service)
):
    """Get aggregated profile from all services"""
    try:
        response = await inter_service.call_service(
            "user-profile-service",
            f"/profile/{user_id}/aggregate",
            method="GET"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/profile/{user_id}/progress")
async def get_user_progress(
    user_id: str,
    inter_service: InterServiceClient = Depends(get_inter_service)
):
    """Get user's progress across all modules"""
    try:
        response = await inter_service.call_service(
            "user-profile-service",
            f"/profile/{user_id}/progress",
            method="GET"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== ADMIN ROUTES ==============

@app.post("/api/v1/admin/services/health")
async def check_all_services_health(
    registry: ServiceRegistry = Depends(get_service_registry),
    inter_service: InterServiceClient = Depends(get_inter_service)
):
    """Check health of all registered services"""
    services_health = {}
    
    for service_name in ["compass-service", "user-profile-service", "skill-analyzer-service", "expertise-analyzer-service"]:
        try:
            service = await registry.get_service(service_name)
            if service:
                health = await inter_service.call_service(
                    service_name,
                    service["health_endpoint"],
                    method="GET"
                )
                services_health[service_name] = {"status": "healthy", "details": health}
            else:
                services_health[service_name] = {"status": "not_registered"}
        except Exception as e:
            services_health[service_name] = {"status": "unhealthy", "error": str(e)}
    
    return services_health

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
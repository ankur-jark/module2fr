"""User Profile Service - Aggregates profiles from all modules"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any
from datetime import datetime
import json
import asyncio

# Add parent directory to path for shared imports
sys.path.append(str(Path(__file__).parent.parent))
from shared.utils import (
    ServiceRegistry, 
    EventSubscriber, 
    EventPublisher,
    CacheManager,
    get_redis_client
)
from shared.schemas import (
    ProfileComponent,
    AggregatedProfile,
    ModuleProgress,
    ModuleStatus
)

load_dotenv()

# Global instances
app_state = {}

# In-memory storage (replace with database in production)
user_profiles: Dict[str, AggregatedProfile] = {}
module_progress: Dict[str, Dict[str, ModuleProgress]] = {}

async def event_listener():
    """Background task to listen for profile component events"""
    subscriber = app_state["event_subscriber"]
    await subscriber.subscribe(["profile.component.ready", "module.started", "module.completed"])
    
    async for event in subscriber.listen():
        try:
            if event.get("event_type") == "profile_component_ready":
                await handle_profile_component(event)
            elif event.get("event_type") == "module_started":
                await handle_module_started(event)
            elif event.get("event_type") == "module_completed":
                await handle_module_completed(event)
        except Exception as e:
            print(f"Error handling event: {e}")

async def handle_profile_component(event: Dict[str, Any]):
    """Handle incoming profile component from a service"""
    user_id = event.get("user_id")
    component_data = event.get("component")
    
    if not user_id or not component_data:
        return
    
    component = ProfileComponent(**component_data)
    
    # Get or create user profile
    if user_id not in user_profiles:
        user_profiles[user_id] = AggregatedProfile(
            user_id=user_id,
            components={},
            last_updated=datetime.utcnow(),
            completion_status={}
        )
    
    # Add/update component
    profile = user_profiles[user_id]
    profile.components[component.component_type] = component
    profile.last_updated = datetime.utcnow()
    profile.completion_status[component.service_origin] = "completed"
    
    # Cache the updated profile
    cache = app_state.get("cache")
    if cache:
        await cache.set(f"profile:{user_id}", profile.dict(), ttl=3600)
    
    print(f"Updated profile for user {user_id} with {component.component_type}")

async def handle_module_started(event: Dict[str, Any]):
    """Handle module started event"""
    user_id = event.get("user_id")
    module = event.get("module")
    
    if not user_id or not module:
        return
    
    if user_id not in module_progress:
        module_progress[user_id] = {}
    
    module_progress[user_id][module] = ModuleProgress(
        user_id=user_id,
        module_name=module,
        status=ModuleStatus.IN_PROGRESS,
        progress_percentage=0,
        start_time=datetime.utcnow()
    )

async def handle_module_completed(event: Dict[str, Any]):
    """Handle module completed event"""
    user_id = event.get("user_id")
    module = event.get("module")
    
    if user_id in module_progress and module in module_progress[user_id]:
        progress = module_progress[user_id][module]
        progress.status = ModuleStatus.COMPLETED
        progress.progress_percentage = 100
        progress.end_time = datetime.utcnow()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    redis_client = await get_redis_client()
    
    app_state["redis"] = redis_client
    app_state["service_registry"] = ServiceRegistry(redis_client)
    app_state["event_subscriber"] = EventSubscriber(redis_client)
    app_state["event_publisher"] = EventPublisher(redis_client)
    app_state["cache"] = CacheManager(redis_client)
    
    # Register this service
    await app_state["service_registry"].register_service(
        "user-profile-service",
        os.getenv("PROFILE_HOST", "localhost"),
        int(os.getenv("PROFILE_PORT", "8002")),
        "/health"
    )
    
    # Start event listener in background
    app_state["listener_task"] = asyncio.create_task(event_listener())
    
    yield
    
    # Shutdown
    app_state["listener_task"].cancel()
    await app_state["service_registry"].deregister_service("user-profile-service")
    await redis_client.close()

app = FastAPI(
    title="User Profile Service",
    description="Aggregates user profiles from all modules",
    version="1.0.0",
    lifespan=lifespan
)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "user-profile-service",
        "version": "1.0.0",
        "profiles_cached": len(user_profiles)
    }

# Get aggregated profile
@app.get("/profile/{user_id}/aggregate")
async def get_aggregated_profile(user_id: str):
    """Get complete aggregated profile for a user"""
    # Try cache first
    cache = app_state.get("cache")
    if cache:
        cached = await cache.get(f"profile:{user_id}")
        if cached:
            return cached
    
    # Get from memory
    if user_id in user_profiles:
        profile = user_profiles[user_id]
        return profile.dict()
    
    return {
        "user_id": user_id,
        "components": {},
        "completion_status": {},
        "message": "No profile data available yet"
    }

# Get specific component
@app.get("/profile/{user_id}/component/{component_type}")
async def get_profile_component(user_id: str, component_type: str):
    """Get specific profile component"""
    if user_id in user_profiles:
        profile = user_profiles[user_id]
        if component_type in profile.components:
            return profile.components[component_type].dict()
    
    raise HTTPException(status_code=404, detail="Component not found")

# Get user progress
@app.get("/profile/{user_id}/progress")
async def get_user_progress(user_id: str):
    """Get user's progress across all modules"""
    progress_data = module_progress.get(user_id, {})
    
    # Add default progress for known modules
    all_modules = ["compass", "skill-analyzer", "expertise-analyzer"]
    result = {}
    
    for module in all_modules:
        if module in progress_data:
            result[module] = progress_data[module].dict()
        else:
            result[module] = {
                "module_name": module,
                "status": "not_started",
                "progress_percentage": 0
            }
    
    return {
        "user_id": user_id,
        "modules": result,
        "overall_completion": _calculate_overall_completion(result)
    }

# Update progress manually (for modules that don't emit events)
@app.post("/profile/{user_id}/progress/{module_name}")
async def update_module_progress(
    user_id: str,
    module_name: str,
    progress_data: Dict[str, Any]
):
    """Manually update module progress"""
    if user_id not in module_progress:
        module_progress[user_id] = {}
    
    module_progress[user_id][module_name] = ModuleProgress(
        user_id=user_id,
        module_name=module_name,
        status=progress_data.get("status", ModuleStatus.IN_PROGRESS),
        progress_percentage=progress_data.get("progress_percentage", 0),
        start_time=progress_data.get("start_time", datetime.utcnow()),
        end_time=progress_data.get("end_time"),
        metadata=progress_data.get("metadata", {})
    )
    
    return {"message": "Progress updated", "module": module_name}

# Get all users with profiles
@app.get("/profiles/all")
async def get_all_profiles():
    """Get list of all users with profiles"""
    return {
        "total_users": len(user_profiles),
        "users": [
            {
                "user_id": user_id,
                "components": list(profile.components.keys()),
                "last_updated": profile.last_updated
            }
            for user_id, profile in user_profiles.items()
        ]
    }

def _calculate_overall_completion(modules: Dict[str, Any]) -> float:
    """Calculate overall completion percentage"""
    if not modules:
        return 0.0
    
    total = 0
    for module_data in modules.values():
        if isinstance(module_data, dict):
            total += module_data.get("progress_percentage", 0)
    
    return total / len(modules) if modules else 0

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PROFILE_PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)
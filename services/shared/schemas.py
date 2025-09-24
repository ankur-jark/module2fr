"""Shared schemas used across all microservices"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# User related shared schemas
class UserContext(BaseModel):
    """Shared user context across all services"""
    user_id: str
    age: Optional[int] = None
    education_level: Optional[str] = None
    current_status: Optional[str] = None
    location: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)

# Service communication schemas
class ServiceRequest(BaseModel):
    """Standard request format for inter-service communication"""
    request_id: str
    user_id: str
    service_name: str
    action: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ServiceResponse(BaseModel):
    """Standard response format for inter-service communication"""
    request_id: str
    service_name: str
    status: str  # success, error, partial
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Profile components that can be aggregated
class ProfileComponent(BaseModel):
    """Base class for any profile component from any service"""
    component_type: str
    service_origin: str
    confidence: float = Field(ge=0, le=100)
    data: Dict[str, Any]
    generated_at: datetime
    version: str = "1.0"

# Aggregated user profile
class AggregatedProfile(BaseModel):
    """Complete user profile aggregating all services' outputs"""
    user_id: str
    components: Dict[str, ProfileComponent]  # key: component_type
    last_updated: datetime
    completion_status: Dict[str, str]  # service_name: status

# Event schemas for async communication
class ServiceEvent(BaseModel):
    """Event structure for message broker communication"""
    event_id: str
    event_type: str
    service_origin: str
    user_id: Optional[str] = None
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Module status tracking
class ModuleStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

class ModuleProgress(BaseModel):
    """Track progress across different modules"""
    user_id: str
    module_name: str
    status: ModuleStatus
    progress_percentage: float = Field(ge=0, le=100)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
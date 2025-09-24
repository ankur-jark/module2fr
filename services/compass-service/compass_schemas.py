from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Literal, Any
from datetime import datetime
from enum import Enum

class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high_school"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    OTHER = "other"

class UserStatus(str, Enum):
    WORKING = "working"
    STUDENT = "student"
    EXPLORING = "exploring"
    TRANSITIONING = "transitioning"

class QuestionStyle(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"

class JourneyStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class DecisionType(str, Enum):
    CONTINUE = "continue"
    CLARIFY = "clarify"
    COMPLETE = "complete"
    SAVE_PARTIAL = "save_partial"

class UserDemographics(BaseModel):
    age: int = Field(..., ge=16, le=80)
    education_level: Optional[EducationLevel] = None
    current_status: Optional[UserStatus] = None
    location: Optional[str] = None

class UserPreferences(BaseModel):
    language: str = Field(default="en")
    question_style: QuestionStyle = Field(default=QuestionStyle.CASUAL)
    time_available: str = Field(default="15-20 minutes")

class JourneyInitRequest(BaseModel):
    user_id: str
    demographics: UserDemographics
    preferences: UserPreferences = Field(default_factory=UserPreferences)

class RIASECScore(BaseModel):
    realistic: float = Field(default=0.0, ge=0, le=100)
    investigative: float = Field(default=0.0, ge=0, le=100)
    artistic: float = Field(default=0.0, ge=0, le=100)
    social: float = Field(default=0.0, ge=0, le=100)
    enterprising: float = Field(default=0.0, ge=0, le=100)
    conventional: float = Field(default=0.0, ge=0, le=100)

class RIASECConfidence(BaseModel):
    realistic: float = Field(default=0.0, ge=0, le=100)
    investigative: float = Field(default=0.0, ge=0, le=100)
    artistic: float = Field(default=0.0, ge=0, le=100)
    social: float = Field(default=0.0, ge=0, le=100)
    enterprising: float = Field(default=0.0, ge=0, le=100)
    conventional: float = Field(default=0.0, ge=0, le=100)

class CareerMotivator(BaseModel):
    type: str
    strength: float = Field(ge=1, le=10)
    evidence: str
    confidence: float = Field(ge=0, le=100)

class Interest(BaseModel):
    category: Optional[str] = None
    area: Optional[str] = None  # Legacy field for backward compatibility
    specific: Optional[str] = None
    weight: Optional[float] = None  # Legacy field for backward compatibility
    enthusiasm: Optional[float] = Field(default=None, ge=1, le=10)
    
    def model_post_init(self, __context):
        # Handle legacy format conversion
        if self.area and not self.category:
            self.category = self.area
        if self.weight is not None and self.enthusiasm is None:
            self.enthusiasm = self.weight
        if self.specific is None and self.category:
            self.specific = f"General interest in {self.category}"

class QuestionTarget(BaseModel):
    primary_dimension: str
    secondary_dimensions: List[str] = Field(default_factory=list)
    reason: str

class OptionTarget(BaseModel):
    id: str  # A, B, C, D
    text: str
    riasec_weights: Dict[str, float] = Field(default_factory=dict)  # realistic: 0.8, etc
    motivators: List[Dict[str, Any]] = Field(default_factory=list)  # [{type: "autonomy", weight: 0.7}]
    interests: List[Dict[str, Any]] = Field(default_factory=list)  # [{area: "technology", weight: 0.6}]
    confidence_impact: float = Field(default=0.0)  # How much this clarifies understanding
    
class GeneratedQuestion(BaseModel):
    question_id: str
    question_number: int
    question_text: str
    target_dimensions: QuestionTarget
    options: List[OptionTarget] = Field(default_factory=list)  # Options with their targets
    context_note: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(BaseModel):
    question_id: str
    response_text: str
    response_time_seconds: Optional[int] = None
    skipped: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ResponseAnalysis(BaseModel):
    riasec_signals: Dict[str, Dict[str, Any]]
    motivators: List[CareerMotivator]
    interests: List[Interest]
    response_quality: Literal["high", "medium", "low"]
    contradictions: List[str] = Field(default_factory=list)
    strong_signals: List[str] = Field(default_factory=list)

class ConfidenceScore(BaseModel):
    riasec_confidence: RIASECConfidence
    motivator_confidence: float = Field(ge=0, le=100)
    interest_confidence: float = Field(ge=0, le=100)
    overall_confidence: float = Field(ge=0, le=100)
    ready_to_complete: bool
    gaps_remaining: List[str] = Field(default_factory=list)

class JourneyDecision(BaseModel):
    decision: DecisionType
    reasoning: str
    next_focus: Optional[str] = None
    confidence_score: ConfidenceScore

class ProfileInsights(BaseModel):
    summary: str
    strengths: List[str]
    ideal_environment: str
    career_direction: str
    unique_combinations: List[str]
    potential_blind_spots: List[str]

class CompletedProfile(BaseModel):
    user_id: str
    journey_id: str
    riasec_profile: RIASECScore
    riasec_code: str  # e.g., "RIA"
    motivators: Dict[str, List[str]]  # {"top": [...], "moderate": [...], "low": [...]}
    interests: Dict[str, List[str]]  # {"primary": [...], "secondary": [...], "emerging": [...]}
    insights: ProfileInsights
    completion_date: datetime
    questions_answered: int
    journey_duration_minutes: float
    confidence_at_completion: float

class JourneyState(BaseModel):
    journey_id: str
    user_id: str
    status: JourneyStatus
    demographics: Optional[UserDemographics] = None
    preferences: Optional[UserPreferences] = None
    current_question_number: int = Field(default=0)
    questions_asked: List[GeneratedQuestion] = Field(default_factory=list)
    responses: List[UserResponse] = Field(default_factory=list)
    analyses: List[ResponseAnalysis] = Field(default_factory=list)
    current_profile: RIASECScore = Field(default_factory=RIASECScore)
    current_confidence: Optional[ConfidenceScore] = None
    identified_motivators: List[CareerMotivator] = Field(default_factory=list)
    identified_interests: List[Interest] = Field(default_factory=list)
    clarifications_used: int = Field(default=0)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    completed_profile: Optional[CompletedProfile] = None
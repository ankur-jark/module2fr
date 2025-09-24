import uuid
from typing import Optional
from datetime import datetime
from openai import AsyncOpenAI
import redis.asyncio as redis
import json

from compass_schemas import (
    JourneyInitRequest,
    JourneyState,
    JourneyStatus,
    GeneratedQuestion,
    UserResponse,
    ResponseAnalysis,
    JourneyDecision,
    DecisionType,
    CompletedProfile,
    ConfidenceScore
)
from question_generator import QuestionGeneratorService
from response_analyzer import ResponseAnalyzerService
from confidence_scorer import ConfidenceScorerService
from decision_engine import DecisionEngineService
from profile_synthesizer import ProfileSynthesizerService

class CompassOrchestrator:
    def __init__(
        self,
        openai_client: AsyncOpenAI,
        redis_client: redis.Redis,
        event_publisher=None
    ):
        self.openai_client = openai_client
        self.redis_client = redis_client
        self.event_publisher = event_publisher
        
        # Initialize all services
        self.question_generator = QuestionGeneratorService(openai_client)
        self.response_analyzer = ResponseAnalyzerService(openai_client)
        self.confidence_scorer = ConfidenceScorerService()
        self.decision_engine = DecisionEngineService()
        self.profile_synthesizer = ProfileSynthesizerService(openai_client)
        
        # Cache settings
        self.cache_ttl = 3600  # 1 hour
    
    async def start_journey(self, request: JourneyInitRequest) -> JourneyState:
        # Create new journey state
        journey_id = str(uuid.uuid4())
        journey_state = JourneyState(
            journey_id=journey_id,
            user_id=request.user_id,
            status=JourneyStatus.IN_PROGRESS,
            demographics=request.demographics,
            preferences=request.preferences,
            current_question_number=0,
            questions_asked=[],
            responses=[],
            analyses=[],
            clarifications_used=0,
            start_time=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        # Save initial state
        await self._save_journey_state(journey_state)
        
        # Publish journey started event
        await self._publish_event("journey.started", {
            "journey_id": journey_id,
            "user_id": request.user_id,
            "demographics": request.demographics.model_dump(),
            "preferences": request.preferences.model_dump()
        })
        
        # Generate first question
        first_question = await self.generate_next_question(
            journey_id,
            request.demographics,
            request.preferences
        )
        
        return journey_state
    
    async def generate_next_question(
        self,
        journey_id: str,
        demographics=None,
        preferences=None
    ) -> GeneratedQuestion:
        # Load journey state
        journey_state = await self._load_journey_state(journey_id)
        if not journey_state:
            raise ValueError(f"Journey {journey_id} not found")
        
        # Use stored demographics and preferences if not provided
        demographics = demographics or journey_state.demographics
        preferences = preferences or journey_state.preferences
        
        # Generate question using the service
        question = await self.question_generator.generate_question(
            journey_state,
            demographics,
            preferences
        )
        
        # Update journey state
        journey_state.questions_asked.append(question)
        journey_state.current_question_number = len(journey_state.questions_asked)
        journey_state.last_updated = datetime.utcnow()
        
        # Track if this is a clarification
        if journey_state.current_question_number > 15:
            journey_state.clarifications_used += 1
        
        # Save updated state
        await self._save_journey_state(journey_state)
        
        # Publish event
        await self._publish_event("question.generated", {
            "journey_id": journey_id,
            "question_id": question.question_id,
            "question_number": question.question_number,
            "is_clarification": journey_state.current_question_number > 15
        })
        
        return question
    
    async def process_response(
        self,
        journey_id: str,
        question_id: str,
        response_text: str,
        response_time_seconds: Optional[int] = None,
        skipped: bool = False
    ) -> JourneyDecision:
        # Load journey state
        journey_state = await self._load_journey_state(journey_id)
        if not journey_state:
            raise ValueError(f"Journey {journey_id} not found")
        
        # Find the question
        question = next(
            (q for q in journey_state.questions_asked if q.question_id == question_id),
            None
        )
        if not question:
            raise ValueError(f"Question {question_id} not found in journey")
        
        # Create user response
        user_response = UserResponse(
            question_id=question_id,
            response_text=response_text,
            response_time_seconds=response_time_seconds,
            skipped=skipped,
            timestamp=datetime.utcnow()
        )
        
        # Analyze the response
        analysis = await self.response_analyzer.analyze_response(
            user_response,
            question
        )
        
        # Update journey state
        journey_state.responses.append(user_response)
        journey_state.analyses.append(analysis)
        
        # Update current profile (aggregate RIASEC scores)
        self._update_current_profile(journey_state)
        
        # Calculate confidence
        confidence_score = self.confidence_scorer.calculate_confidence(journey_state)
        journey_state.current_confidence = confidence_score
        
        # Make decision on next step - use updated confidence if available
        decision = self.decision_engine.make_decision(
            journey_state, 
            journey_state.current_confidence or confidence_score
        )
        
        # Handle decision outcomes
        if decision.decision == DecisionType.COMPLETE:
            await self._complete_journey(journey_state)
        elif decision.decision == DecisionType.SAVE_PARTIAL:
            await self._save_partial_profile(journey_state)
        
        # Save updated state
        journey_state.last_updated = datetime.utcnow()
        await self._save_journey_state(journey_state)
        
        # Publish event
        await self._publish_event("response.processed", {
            "journey_id": journey_id,
            "question_id": question_id,
            "skipped": skipped,
            "decision": decision.decision,
            "confidence": confidence_score.overall_confidence
        })
        
        return decision
    
    async def complete_journey(self, journey_id: str) -> CompletedProfile:
        # Load journey state
        journey_state = await self._load_journey_state(journey_id)
        if not journey_state:
            raise ValueError(f"Journey {journey_id} not found")
        
        return await self._complete_journey(journey_state)
    
    async def get_journey_state(self, journey_id: str) -> Optional[JourneyState]:
        return await self._load_journey_state(journey_id)
    
    async def abandon_journey(self, journey_id: str) -> JourneyState:
        journey_state = await self._load_journey_state(journey_id)
        if not journey_state:
            raise ValueError(f"Journey {journey_id} not found")
        
        journey_state.status = JourneyStatus.ABANDONED
        journey_state.last_updated = datetime.utcnow()
        
        await self._save_journey_state(journey_state)
        
        await self._publish_event("journey.abandoned", {
            "journey_id": journey_id,
            "questions_answered": len(journey_state.responses)
        })
        
        return journey_state
    
    async def update_journey_profile(
        self,
        journey_id: str,
        profile_update: Optional[object] = None,
        confidence_update: Optional[ConfidenceScore] = None
    ) -> JourneyState:
        """Update journey profile and confidence values"""
        journey_state = await self._load_journey_state(journey_id)
        if not journey_state:
            raise ValueError(f"Journey {journey_id} not found")
        
        # RAISEC profile updates are no longer tracked in orchestrator
        
        # Update confidence if provided
        if confidence_update:
            journey_state.current_confidence = confidence_update
        
        # Update timestamp
        journey_state.last_updated = datetime.utcnow()
        
        # Save updated state
        await self._save_journey_state(journey_state)
        
        # Publish event without RAISEC-specific flags
        await self._publish_event("profile.updated", {
            "journey_id": journey_id,
            "user_id": journey_state.user_id,
            "confidence_updated": confidence_update is not None
        })
        
        return journey_state
    
    # Private helper methods
    
    def _update_current_profile(self, journey_state: JourneyState):
        # Aggregate motivators (store the most recent ones with highest strength)
        all_motivators = []
        for analysis in journey_state.analyses:
            all_motivators.extend(analysis.motivators)
        
        # Sort by strength and deduplicate
        seen_types = set()
        unique_motivators = []
        for motivator in sorted(all_motivators, key=lambda x: x.strength, reverse=True):
            if motivator.type not in seen_types:
                seen_types.add(motivator.type)
                unique_motivators.append(motivator)
        
        journey_state.identified_motivators = unique_motivators[:12]  # Keep top 12
        
        # Aggregate interests (most recent with highest enthusiasm)
        all_interests = []
        for analysis in journey_state.analyses:
            all_interests.extend(analysis.interests)
        
        # Sort by enthusiasm and deduplicate by category
        seen_categories = set()
        unique_interests = []
        for interest in sorted(all_interests, key=lambda x: x.enthusiasm, reverse=True):
            if interest.category not in seen_categories:
                seen_categories.add(interest.category)
                unique_interests.append(interest)
        
        journey_state.identified_interests = unique_interests[:20]  # Keep top 20
    
    async def _complete_journey(self, journey_state: JourneyState) -> CompletedProfile:
        # Synthesize the final profile
        completed_profile = await self.profile_synthesizer.synthesize_profile(journey_state)
        
        # Update journey state
        journey_state.status = JourneyStatus.COMPLETED
        journey_state.completed_profile = completed_profile
        journey_state.last_updated = datetime.utcnow()
        
        # Save state
        await self._save_journey_state(journey_state)
        
        # Publish completion event
        await self._publish_event("journey.completed", {
            "journey_id": journey_state.journey_id,
            "user_id": journey_state.user_id,
            "confidence": completed_profile.confidence_at_completion,
            "duration_minutes": completed_profile.journey_duration_minutes
        })
        
        return completed_profile
    
    async def _save_partial_profile(self, journey_state: JourneyState):
        # Similar to complete but with partial flag
        journey_state.status = JourneyStatus.ABANDONED
        # Could create a partial profile here if needed
        await self._save_journey_state(journey_state)
    
    async def _save_journey_state(self, journey_state: JourneyState):
        # Save to Redis cache
        key = f"compass:journey:{journey_state.journey_id}"
        value = journey_state.model_dump_json()
        await self.redis_client.setex(key, self.cache_ttl, value)
    
    async def _load_journey_state(self, journey_id: str) -> Optional[JourneyState]:
        import logging
        logger = logging.getLogger(__name__)
        
        # Load from Redis cache
        key = f"compass:journey:{journey_id}"
        logger.info(f"Loading journey state for key: {key}")
        
        value = await self.redis_client.get(key)
        
        if value:
            logger.info(f"Found journey data, attempting to deserialize")
            try:
                return JourneyState.model_validate_json(value)
            except Exception as e:
                logger.error(f"Failed to deserialize journey state: {str(e)}")
                logger.error(f"Raw value: {value[:500] if value else 'None'}")
                raise
        
        logger.warning(f"No journey found with key: {key}")
        return None
    
    async def _publish_event(self, event_type: str, data: dict):
        if self.event_publisher:
            await self.event_publisher.publish(event_type, {
                **data,
                "timestamp": datetime.utcnow().isoformat()
            })
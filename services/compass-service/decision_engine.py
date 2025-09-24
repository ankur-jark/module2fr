from compass_schemas import (
    JourneyDecision,
    DecisionType,
    ConfidenceScore,
    JourneyState
)
from typing import Optional

class DecisionEngineService:
    def __init__(self):
        self.min_questions = 12
        self.standard_questions = 15
        self.max_clarifications = 3
        self.high_confidence_threshold = 85.0
        self.acceptable_confidence_threshold = 75.0
        self.minimum_confidence_threshold = 60.0
        
    def make_decision(
        self,
        journey_state: JourneyState,
        confidence_score: ConfidenceScore
    ) -> JourneyDecision:
        
        questions_asked = journey_state.current_question_number
        clarifications_used = journey_state.clarifications_used
        overall_confidence = confidence_score.overall_confidence
        
        # Check for abandonment signals (too many skips)
        skip_rate = self._calculate_skip_rate(journey_state)
        if skip_rate > 0.5 and questions_asked >= 5:
            return self._create_save_partial_decision(
                confidence_score,
                "High skip rate detected - saving partial profile"
            )
        
        # Main decision logic
        decision_type, reasoning, next_focus = self._determine_decision(
            questions_asked,
            clarifications_used,
            overall_confidence,
            confidence_score
        )
        
        return JourneyDecision(
            decision=decision_type,
            reasoning=reasoning,
            next_focus=next_focus,
            confidence_score=confidence_score
        )
    
    def _determine_decision(
        self,
        questions_asked: int,
        clarifications_used: int,
        overall_confidence: float,
        confidence_score: ConfidenceScore
    ) -> tuple[DecisionType, str, Optional[str]]:
        
        # Early completion scenario - high confidence achieved early
        if questions_asked >= self.min_questions and overall_confidence >= self.high_confidence_threshold:
            return (
                DecisionType.COMPLETE,
                f"High confidence achieved ({overall_confidence:.0f}%) after {questions_asked} questions",
                None
            )
        
        # Standard flow - haven't reached 15 questions yet
        if questions_asked < self.standard_questions:
            if overall_confidence < self.high_confidence_threshold:
                next_focus = self._identify_next_focus(confidence_score)
                return (
                    DecisionType.CONTINUE,
                    f"Continuing assessment (question {questions_asked + 1}/15, confidence: {overall_confidence:.0f}%)",
                    next_focus
                )
            else:
                # High confidence but let's get a bit more data
                return (
                    DecisionType.CONTINUE,
                    f"Confidence is high ({overall_confidence:.0f}%) but gathering additional data",
                    "Confirming strong signals and exploring edge cases"
                )
        
        # Reached 15 questions - decision point
        if questions_asked == self.standard_questions:
            if overall_confidence >= self.acceptable_confidence_threshold:
                return (
                    DecisionType.COMPLETE,
                    f"Standard assessment complete with good confidence ({overall_confidence:.0f}%)",
                    None
                )
            elif clarifications_used < self.max_clarifications:
                gaps = confidence_score.gaps_remaining[:2]  # Focus on top 2 gaps
                return (
                    DecisionType.CLARIFY,
                    f"Confidence at {overall_confidence:.0f}% - clarifying key gaps",
                    f"Clarifying: {', '.join(gaps) if gaps else 'lowest confidence areas'}"
                )
            else:
                return (
                    DecisionType.COMPLETE,
                    f"Completing with available data (confidence: {overall_confidence:.0f}%)",
                    None
                )
        
        # In clarification phase (questions 16-18)
        if questions_asked > self.standard_questions:
            if clarifications_used >= self.max_clarifications:
                return (
                    DecisionType.COMPLETE,
                    f"Maximum clarifications reached - completing with {overall_confidence:.0f}% confidence",
                    None
                )
            elif overall_confidence >= self.acceptable_confidence_threshold:
                return (
                    DecisionType.COMPLETE,
                    f"Acceptable confidence achieved ({overall_confidence:.0f}%) after clarifications",
                    None
                )
            else:
                remaining_clarifications = self.max_clarifications - clarifications_used
                if remaining_clarifications > 0:
                    next_gap = confidence_score.gaps_remaining[0] if confidence_score.gaps_remaining else "general clarity"
                    return (
                        DecisionType.CLARIFY,
                        f"Using clarification {clarifications_used + 1}/{self.max_clarifications} to improve confidence",
                        f"Focusing on: {next_gap}"
                    )
                else:
                    return (
                        DecisionType.COMPLETE,
                        f"Completing assessment with {overall_confidence:.0f}% confidence",
                        None
                    )
        
        # Fallback - should not reach here in normal flow
        return (
            DecisionType.COMPLETE,
            f"Assessment complete (confidence: {overall_confidence:.0f}%)",
            None
        )
    
    def _calculate_skip_rate(self, journey_state: JourneyState) -> float:
        if not journey_state.responses:
            return 0.0
        
        skipped = sum(1 for r in journey_state.responses if r.skipped)
        return skipped / len(journey_state.responses)
    
    def _identify_next_focus(self, confidence_score: ConfidenceScore) -> str:
        # Identify what to focus on next based on gaps
        if not confidence_score.gaps_remaining:
            return "Exploring general career preferences"
        
        # Take the most critical gap
        primary_gap = confidence_score.gaps_remaining[0]
        
        # Make it more conversational
        if "Realistic" in primary_gap:
            return "Understanding hands-on and practical interests"
        elif "Investigative" in primary_gap:
            return "Exploring analytical and research interests"
        elif "Artistic" in primary_gap:
            return "Discovering creative and expressive preferences"
        elif "Social" in primary_gap:
            return "Understanding interpersonal and helping motivations"
        elif "Enterprising" in primary_gap:
            return "Exploring leadership and business interests"
        elif "Conventional" in primary_gap:
            return "Understanding organizational and structured work preferences"
        elif "motivators" in primary_gap.lower():
            return "Identifying key career drivers and values"
        elif "interests" in primary_gap.lower():
            return "Discovering specific areas of enthusiasm"
        else:
            return primary_gap
    
    def _create_save_partial_decision(
        self,
        confidence_score: ConfidenceScore,
        reason: str
    ) -> JourneyDecision:
        return JourneyDecision(
            decision=DecisionType.SAVE_PARTIAL,
            reasoning=reason,
            next_focus=None,
            confidence_score=confidence_score
        )
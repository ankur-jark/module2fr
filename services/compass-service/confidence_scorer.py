from typing import List, Dict, Tuple
import numpy as np
from compass_schemas import (
    ConfidenceScore,
    RIASECConfidence,
    ResponseAnalysis,
    UserResponse,
    JourneyState
)

class ConfidenceScorerService:
    def __init__(self):
        self.min_signals_for_confidence = 3
        self.skip_penalty = 10.0
        self.recent_weight_factor = 1.2
        
    def calculate_confidence(self, journey_state: JourneyState) -> ConfidenceScore:
        # Calculate RIASEC confidence
        riasec_confidence = self._calculate_riasec_confidence(journey_state.analyses)
        
        # Calculate motivator confidence
        motivator_confidence = self._calculate_motivator_confidence(journey_state.analyses)
        
        # Calculate interest confidence
        interest_confidence = self._calculate_interest_confidence(journey_state.analyses)
        
        # Adjust for skipped questions
        skip_adjustment = self._calculate_skip_adjustment(journey_state.responses)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(
            riasec_confidence,
            motivator_confidence, 
            interest_confidence,
            skip_adjustment
        )
        
        # Determine if ready to complete
        ready_to_complete = self._is_ready_to_complete(
            overall_confidence,
            journey_state.current_question_number
        )
        
        # Identify remaining gaps
        gaps_remaining = self._identify_gaps(
            riasec_confidence,
            motivator_confidence,
            interest_confidence
        )
        
        return ConfidenceScore(
            riasec_confidence=riasec_confidence,
            motivator_confidence=motivator_confidence,
            interest_confidence=interest_confidence,
            overall_confidence=overall_confidence,
            ready_to_complete=ready_to_complete,
            gaps_remaining=gaps_remaining
        )
    
    def _calculate_riasec_confidence(self, analyses: List[ResponseAnalysis]) -> RIASECConfidence:
        dimensions = ['realistic', 'investigative', 'artistic', 'social', 'enterprising', 'conventional']
        confidence_scores = {}
        
        for dimension in dimensions:
            signals = []
            weights = []
            
            for i, analysis in enumerate(analyses):
                if dimension in analysis.riasec_signals:
                    signal = analysis.riasec_signals[dimension]
                    signals.append(signal['confidence'])
                    # More recent responses get higher weight
                    weight = 1.0 + (i / len(analyses)) * 0.5
                    weights.append(weight)
            
            if signals:
                # Weighted average with consideration for signal count
                weighted_avg = np.average(signals, weights=weights)
                signal_count_bonus = min(len(signals) * 5, 20)  # Max 20% bonus for multiple signals
                confidence = min(weighted_avg + signal_count_bonus, 100)
                
                # Penalize if too few signals
                if len(signals) < self.min_signals_for_confidence:
                    confidence *= (len(signals) / self.min_signals_for_confidence)
            else:
                confidence = 0.0
                
            confidence_scores[dimension] = confidence
        
        return RIASECConfidence(
            realistic=confidence_scores['realistic'],
            investigative=confidence_scores['investigative'],
            artistic=confidence_scores['artistic'],
            social=confidence_scores['social'],
            enterprising=confidence_scores['enterprising'],
            conventional=confidence_scores['conventional']
        )
    
    def _calculate_motivator_confidence(self, analyses: List[ResponseAnalysis]) -> float:
        # Track which motivators we've identified
        identified_motivators = set()
        total_possible_motivators = 12
        
        motivator_strengths = {}
        
        for analysis in analyses:
            for motivator in analysis.motivators:
                identified_motivators.add(motivator.type)
                
                if motivator.type not in motivator_strengths:
                    motivator_strengths[motivator.type] = []
                motivator_strengths[motivator.type].append(motivator.strength)
        
        # Calculate coverage
        coverage = len(identified_motivators) / total_possible_motivators * 100
        
        # Calculate consistency (how consistent are the strengths for each motivator)
        consistency_scores = []
        for strengths in motivator_strengths.values():
            if len(strengths) > 1:
                # Lower std deviation = higher consistency
                std_dev = np.std(strengths)
                consistency = max(0, 100 - (std_dev * 20))
                consistency_scores.append(consistency)
        
        avg_consistency = np.mean(consistency_scores) if consistency_scores else 50
        
        # Combine coverage and consistency
        confidence = (coverage * 0.6) + (avg_consistency * 0.4)
        
        # Need at least 5 motivators identified for decent confidence
        if len(identified_motivators) < 5:
            confidence *= (len(identified_motivators) / 5)
        
        return min(confidence, 100)
    
    def _calculate_interest_confidence(self, analyses: List[ResponseAnalysis]) -> float:
        # Track interests and their frequencies
        interest_categories = {}
        total_interests = 0
        
        for analysis in analyses:
            for interest in analysis.interests:
                total_interests += 1
                if interest.category not in interest_categories:
                    interest_categories[interest.category] = []
                interest_categories[interest.category].append(interest.enthusiasm)
        
        if total_interests == 0:
            return 0.0
        
        # Calculate diversity (number of different categories)
        diversity = len(interest_categories)
        
        # Calculate depth (average enthusiasm and count per category)
        depth_scores = []
        for category, enthusiasms in interest_categories.items():
            avg_enthusiasm = np.mean(enthusiasms)
            count_factor = min(len(enthusiasms) / 3, 1.0)  # Normalize by expecting 3 mentions
            depth = avg_enthusiasm * 10 * count_factor
            depth_scores.append(depth)
        
        avg_depth = np.mean(depth_scores) if depth_scores else 0
        
        # Combine diversity and depth
        # We want at least 3-5 different interest categories
        diversity_score = min(diversity / 5 * 100, 100)
        
        confidence = (diversity_score * 0.4) + (avg_depth * 0.6)
        
        # Need minimum number of interests
        if total_interests < 5:
            confidence *= (total_interests / 5)
        
        return min(confidence, 100)
    
    def _calculate_skip_adjustment(self, responses: List[UserResponse]) -> float:
        skipped_count = sum(1 for r in responses if r.skipped)
        total_count = len(responses)
        
        if total_count == 0:
            return 0
        
        skip_rate = skipped_count / total_count
        # Each skipped question reduces confidence
        adjustment = -(skip_rate * self.skip_penalty * total_count)
        
        return adjustment
    
    def _calculate_overall_confidence(
        self,
        riasec: RIASECConfidence,
        motivator: float,
        interest: float,
        skip_adjustment: float
    ) -> float:
        # Average RIASEC confidence
        riasec_avg = np.mean([
            riasec.realistic,
            riasec.investigative,
            riasec.artistic,
            riasec.social,
            riasec.enterprising,
            riasec.conventional
        ])
        
        # Weighted average (RIASEC is most important)
        base_confidence = (riasec_avg * 0.5) + (motivator * 0.3) + (interest * 0.2)
        
        # Apply skip adjustment
        adjusted_confidence = max(0, base_confidence + skip_adjustment)
        
        return min(adjusted_confidence, 100)
    
    def _is_ready_to_complete(self, overall_confidence: float, questions_asked: int) -> bool:
        # Decision logic based on confidence and questions asked
        if questions_asked >= 12 and overall_confidence >= 85:
            return True
        elif questions_asked >= 15 and overall_confidence >= 75:
            return True
        elif questions_asked >= 18:  # Max with clarifications
            return True
        else:
            return False
    
    def _identify_gaps(
        self,
        riasec: RIASECConfidence,
        motivator_confidence: float,
        interest_confidence: float
    ) -> List[str]:
        gaps = []
        
        # Check RIASEC dimensions
        riasec_scores = {
            'Realistic': riasec.realistic,
            'Investigative': riasec.investigative,
            'Artistic': riasec.artistic,
            'Social': riasec.social,
            'Enterprising': riasec.enterprising,
            'Conventional': riasec.conventional
        }
        
        for dimension, score in riasec_scores.items():
            if score < 60:
                gaps.append(f"{dimension} dimension (confidence: {score:.0f}%)")
        
        # Check motivators
        if motivator_confidence < 70:
            gaps.append(f"Career motivators (confidence: {motivator_confidence:.0f}%)")
        
        # Check interests
        if interest_confidence < 60:
            gaps.append(f"Personal interests (confidence: {interest_confidence:.0f}%)")
        
        return gaps
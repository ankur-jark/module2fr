import json
from typing import List, Dict, Any, Tuple
from datetime import datetime
import numpy as np
from openai import AsyncOpenAI
from compass_schemas import (
    CompletedProfile,
    ProfileInsights,
    RIASECScore,
    JourneyState,
    ResponseAnalysis
)

class ProfileSynthesizerService:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.model = "gpt-4-turbo-preview"
        
    async def synthesize_profile(self, journey_state: JourneyState) -> CompletedProfile:
        # Calculate final RIASEC scores
        riasec_score, riasec_code = self._calculate_final_riasec(journey_state.analyses)
        
        # Organize motivators by priority
        motivators = self._organize_motivators(journey_state.analyses)
        
        # Cluster interests
        interests = self._cluster_interests(journey_state.analyses)
        
        # Generate insights using GPT-4
        insights = await self._generate_insights(
            riasec_score,
            riasec_code,
            motivators,
            interests,
            journey_state
        )
        
        # Calculate journey metrics
        journey_duration = (datetime.utcnow() - journey_state.start_time).total_seconds() / 60
        
        return CompletedProfile(
            user_id=journey_state.user_id,
            journey_id=journey_state.journey_id,
            riasec_profile=riasec_score,
            riasec_code=riasec_code,
            motivators=motivators,
            interests=interests,
            insights=insights,
            completion_date=datetime.utcnow(),
            questions_answered=len([r for r in journey_state.responses if not r.skipped]),
            journey_duration_minutes=journey_duration,
            confidence_at_completion=journey_state.current_confidence.overall_confidence if journey_state.current_confidence else 0
        )
    
    def _calculate_final_riasec(self, analyses: List[ResponseAnalysis]) -> Tuple[RIASECScore, str]:
        dimensions = ['realistic', 'investigative', 'artistic', 'social', 'enterprising', 'conventional']
        final_scores = {}
        
        for dimension in dimensions:
            scores = []
            weights = []
            
            for i, analysis in enumerate(analyses):
                if dimension in analysis.riasec_signals:
                    signal = analysis.riasec_signals[dimension]
                    scores.append(signal['score'])
                    
                    # Weight based on recency and confidence
                    recency_weight = 1.0 + (i / len(analyses)) * 0.5
                    confidence_weight = signal['confidence'] / 100
                    quality_weight = 1.5 if analysis.response_quality == 'high' else 1.0
                    
                    weight = recency_weight * confidence_weight * quality_weight
                    weights.append(weight)
            
            if scores:
                # Weighted average, normalized to 0-100
                weighted_score = np.average(scores, weights=weights) * 10
                final_scores[dimension] = min(weighted_score, 100)
            else:
                final_scores[dimension] = 0
        
        # Create RIASECScore object
        riasec_score = RIASECScore(
            realistic=final_scores['realistic'],
            investigative=final_scores['investigative'],
            artistic=final_scores['artistic'],
            social=final_scores['social'],
            enterprising=final_scores['enterprising'],
            conventional=final_scores['conventional']
        )
        
        # Generate Holland code (top 3 dimensions)
        sorted_dims = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        code_map = {
            'realistic': 'R',
            'investigative': 'I',
            'artistic': 'A',
            'social': 'S',
            'enterprising': 'E',
            'conventional': 'C'
        }
        riasec_code = ''.join([code_map[dim[0]] for dim in sorted_dims[:3]])
        
        return riasec_score, riasec_code
    
    def _organize_motivators(self, analyses: List[ResponseAnalysis]) -> Dict[str, List[str]]:
        # Aggregate all motivator signals
        motivator_scores = {}
        
        for analysis in analyses:
            for motivator in analysis.motivators:
                if motivator.type not in motivator_scores:
                    motivator_scores[motivator.type] = []
                
                # Weight by confidence and strength
                score = motivator.strength * (motivator.confidence / 100)
                motivator_scores[motivator.type].append(score)
        
        # Calculate average scores
        motivator_averages = {}
        for motivator_type, scores in motivator_scores.items():
            motivator_averages[motivator_type] = np.mean(scores)
        
        # Sort by average score
        sorted_motivators = sorted(motivator_averages.items(), key=lambda x: x[1], reverse=True)
        
        # Categorize into top, moderate, and low
        total = len(sorted_motivators)
        if total == 0:
            return {"top": [], "moderate": [], "low": []}
        
        top_threshold = max(3, total // 3)
        moderate_threshold = max(6, (total * 2) // 3)
        
        return {
            "top": [m[0] for m in sorted_motivators[:top_threshold]],
            "moderate": [m[0] for m in sorted_motivators[top_threshold:moderate_threshold]],
            "low": [m[0] for m in sorted_motivators[moderate_threshold:]]
        }
    
    def _cluster_interests(self, analyses: List[ResponseAnalysis]) -> Dict[str, List[str]]:
        # Collect all interests with their enthusiasm scores
        interest_map = {}
        
        for analysis in analyses:
            for interest in analysis.interests:
                key = f"{interest.category}: {interest.specific}"
                if key not in interest_map:
                    interest_map[key] = []
                interest_map[key].append(interest.enthusiasm)
        
        # Calculate average enthusiasm for each interest
        interest_scores = {}
        for interest, scores in interest_map.items():
            interest_scores[interest] = np.mean(scores)
        
        # Sort by enthusiasm
        sorted_interests = sorted(interest_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Categorize
        if not sorted_interests:
            return {"primary": [], "secondary": [], "emerging": []}
        
        # Primary: Top enthusiasm (8+) or top 3
        primary = []
        secondary = []
        emerging = []
        
        for interest, score in sorted_interests:
            if score >= 8 or len(primary) < 3:
                primary.append(interest)
            elif score >= 6 or len(secondary) < 3:
                secondary.append(interest)
            else:
                emerging.append(interest)
        
        return {
            "primary": primary[:5],  # Limit to top 5
            "secondary": secondary[:5],
            "emerging": emerging[:3]
        }
    
    async def _generate_insights(
        self,
        riasec_score: RIASECScore,
        riasec_code: str,
        motivators: Dict[str, List[str]],
        interests: Dict[str, List[str]],
        journey_state: JourneyState
    ) -> ProfileInsights:
        
        # Prepare context for GPT-4
        prompt = self._build_insights_prompt(
            riasec_score,
            riasec_code,
            motivators,
            interests,
            journey_state
        )
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert career psychologist creating personalized insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return ProfileInsights(
            summary=result["summary"],
            strengths=result["strengths"],
            ideal_environment=result["ideal_environment"],
            career_direction=result["career_direction"],
            unique_combinations=result["unique_combinations"],
            potential_blind_spots=result["potential_blind_spots"]
        )
    
    def _build_insights_prompt(
        self,
        riasec_score: RIASECScore,
        riasec_code: str,
        motivators: Dict[str, List[str]],
        interests: Dict[str, List[str]],
        journey_state: JourneyState
    ) -> str:
        
        prompt = f"""Synthesize a comprehensive career profile based on this assessment data:

RIASEC Profile: {riasec_code}
- Realistic: {riasec_score.realistic:.0f}%
- Investigative: {riasec_score.investigative:.0f}%
- Artistic: {riasec_score.artistic:.0f}%
- Social: {riasec_score.social:.0f}%
- Enterprising: {riasec_score.enterprising:.0f}%
- Conventional: {riasec_score.conventional:.0f}%

Top Career Motivators: {', '.join(motivators.get('top', []))}
Moderate Motivators: {', '.join(motivators.get('moderate', []))}

Primary Interests: {', '.join(interests.get('primary', []))}
Secondary Interests: {', '.join(interests.get('secondary', []))}

Questions Answered: {len(journey_state.responses)}
Response Quality: {self._assess_overall_quality(journey_state.analyses)}

Generate personalized insights that:
1. Synthesize the overall career personality
2. Identify key strengths based on the profile
3. Describe the ideal work environment
4. Suggest career directions (general, not specific jobs)
5. Note unique combinations that stand out
6. Identify potential blind spots or areas for growth

Output as JSON:
{{
  "summary": "2-3 sentence overview of their career personality",
  "strengths": ["strength1", "strength2", "strength3", "strength4"],
  "ideal_environment": "Description of ideal work environment in 2-3 sentences",
  "career_direction": "General career guidance in 2-3 sentences",
  "unique_combinations": ["unique aspect 1", "unique aspect 2"],
  "potential_blind_spots": ["blind spot 1", "blind spot 2"]
}}

Make insights specific to their profile, not generic. Reference their actual scores and preferences."""
        
        return prompt
    
    def _assess_overall_quality(self, analyses: List[ResponseAnalysis]) -> str:
        if not analyses:
            return "unknown"
        
        quality_scores = {
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        total_score = sum(quality_scores.get(a.response_quality, 1) for a in analyses)
        avg_score = total_score / len(analyses)
        
        if avg_score >= 2.5:
            return "High quality responses overall"
        elif avg_score >= 1.8:
            return "Good quality responses overall"
        else:
            return "Mixed quality responses"
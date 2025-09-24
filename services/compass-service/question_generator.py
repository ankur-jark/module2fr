import json
import logging
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from compass_schemas import (
    GeneratedQuestion,
    QuestionTarget,
    OptionTarget,
    ConfidenceScore,
    JourneyState,
    UserDemographics,
    UserPreferences
)
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class QuestionGeneratorService:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.model = "gpt-4-turbo-preview"
        self.used_question_themes = set()  # Track used themes to prevent repetition
        
    async def generate_question(
        self,
        journey_state: JourneyState,
        demographics: UserDemographics,
        preferences: UserPreferences
    ) -> GeneratedQuestion:
        
        question_number = len(journey_state.questions_asked) + 1
        is_clarification = question_number > 15
        
        # Identify gaps and target dimensions
        target_dimensions = self._identify_target_dimensions(journey_state.current_confidence)
        
        # Build context from previous responses
        context = self._build_context(journey_state)
        
        # Generate the question using GPT-4
        prompt = self._build_generation_prompt(
            demographics=demographics,
            preferences=preferences,
            question_number=question_number,
            is_clarification=is_clarification,
            target_dimensions=target_dimensions,
            context=context
        )
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert career counselor conducting a discovery session."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.debug(f"GPT-4 response: {json.dumps(result, indent=2)}")
        
        # Validate and clean the response
        result = self._validate_and_clean_response(result)
        
        # Extract question and options with metadata
        question_text = result.get("question", "Tell me about your career preferences.")
        
        # Parse options with their target metadata
        option_targets = []
        options = result.get("options", [])
        targets_data = result.get("option_targets", [])
        
        for i, option in enumerate(options):
            option_id = option.get('id', chr(65 + i))
            option_text = option.get('text', str(option))
            
            # Get target metadata for this option (from GPT-4 or apply defaults)
            if i < len(targets_data):
                target = targets_data[i]
            else:
                # Apply intelligent defaults based on option text analysis
                target = self._analyze_option_targets(option_text)
            
            option_targets.append(OptionTarget(
                id=option_id,
                text=option_text,
                riasec_weights={},  # Empty since we're not using RIASEC
                motivators=target.get('motivators', []),
                interests=target.get('interests', []),
                confidence_impact=target.get('confidence_impact', 5.0)
            ))
        
        # Track question theme to prevent repetition
        question_theme = result.get("theme", question_text[:50])
        self.used_question_themes.add(question_theme)
        
        return GeneratedQuestion(
            question_id=str(uuid.uuid4()),
            question_number=question_number,
            question_text=question_text.strip(),
            target_dimensions=QuestionTarget(
                primary_dimension="interests_motivators",
                secondary_dimensions=["motivators", "interests"],
                reason=result.get("context_note", "Exploring interests and motivators")
            ),
            options=option_targets,
            context_note=result.get("context_note", "Focus on interests and motivators"),
            timestamp=datetime.utcnow()
        )
    
    def _identify_target_dimensions(self, confidence: Optional[ConfidenceScore]) -> Dict[str, List[str]]:
        # Since we're not using RIASEC, focus on broad exploration of interests and motivators
        return {
            "primary": ["interests_exploration"],
            "secondary": ["motivators_identification"]
        }
    
    def _build_context(self, journey_state: JourneyState) -> str:
        if not journey_state.responses:
            return "This is the first question in the journey."
        
        context_parts = []
        
        # Note any patterns in interests
        if journey_state.analyses:
            recent_interests = []
            for analysis in journey_state.analyses[-3:]:  # Last 3 responses
                recent_interests.extend([i.category for i in analysis.interests])
            
            if recent_interests:
                unique_interests = list(set(recent_interests))
                context_parts.append(f"Recent interests: {', '.join(unique_interests[:3])}")
        
        # Note motivators patterns if available
        if journey_state.analyses and hasattr(journey_state.analyses[0], 'motivators'):
            recent_motivators = []
            for analysis in journey_state.analyses[-2:]:
                recent_motivators.extend([m.type for m in analysis.motivators])
            
            if recent_motivators:
                unique_motivators = list(set(recent_motivators))
                context_parts.append(f"Emerging motivators: {', '.join(unique_motivators[:2])}")
        
        return " ".join(context_parts) if context_parts else "Building understanding of interests and motivators."
    
    def _build_generation_prompt(
        self,
        demographics: UserDemographics,
        preferences: UserPreferences,
        question_number: int,
        is_clarification: bool,
        target_dimensions: Dict[str, any],
        context: str
    ) -> str:
        
        style_instruction = "conversational and friendly" if preferences.question_style == "casual" else "professional and clear"
        
        # Get list of previously used themes to avoid repetition
        avoid_themes = list(self.used_question_themes)[:5] if self.used_question_themes else []
        avoid_instruction = f"IMPORTANT: Create a UNIQUE scenario. DO NOT repeat these themes: {', '.join(avoid_themes)}" if avoid_themes else ""
        
        prompt = f"""Generate ONE engaging MCQ scenario for a {demographics.age}-year-old {demographics.current_status or 'person'}.

Question #{question_number} of 15 {"(Clarification)" if is_clarification else ""}

{avoid_instruction}

CRITICAL: Design a scenario with 4 response options that reveal career interests and motivators.

**STRICT REQUIREMENTS:**
- Do NOT include any RAISEC fields (e.g., riasec, riasec_weights, realistic, investigative, artistic, social, enterprising, conventional)
- Focus ONLY on interests and motivators
- Each option should contain 2-3 sentences of rich behavioral detail
- Options should be equally appealing but show different preference patterns
- Feel realistic for a {demographics.age}-year-old Indian context

Each option should naturally reveal:
- Career motivators (Autonomy, Achievement, Recognition, Growth, Stability, Purpose, Creativity, Challenge, Money, Team, Work-Life Balance)
- Specific interests and activities (Technology, Business, Social Impact, Arts, Science, Education, Healthcare, Sports, Environment, Entertainment)

Output as JSON with this EXACT structure (NO RAISEC FIELDS ALLOWED):
{{
  "question": "engaging scenario question text",
  "theme": "unique_theme_identifier",
  "options": [
    {{"id": "A", "text": "detailed option text with behavioral details"}},
    {{"id": "B", "text": "detailed option text with behavioral details"}},
    {{"id": "C", "text": "detailed option text with behavioral details"}},
    {{"id": "D", "text": "detailed option text with behavioral details"}}
  ],
  "option_targets": [
    {{
      "motivators": [
        {{"type": "autonomy", "weight": 0.8}},
        {{"type": "money", "weight": 0.7}}
      ],
      "interests": [
        {{"area": "technology", "weight": 0.8}},
        {{"area": "entrepreneurship", "weight": 0.9}}
      ],
      "confidence_impact": 7.0
    }},
    {{
      "motivators": [
        {{"type": "growth", "weight": 0.8}},
        {{"type": "purpose", "weight": 0.7}}
      ],
      "interests": [
        {{"area": "research", "weight": 0.9}},
        {{"area": "sustainability", "weight": 0.7}}
      ],
      "confidence_impact": 7.0
    }},
    {{
      "motivators": [
        {{"type": "creativity", "weight": 0.9}},
        {{"type": "autonomy", "weight": 0.8}}
      ],
      "interests": [
        {{"area": "arts", "weight": 0.9}},
        {{"area": "travel", "weight": 0.7}}
      ],
      "confidence_impact": 7.0
    }},
    {{
      "motivators": [
        {{"type": "purpose", "weight": 0.9}},
        {{"type": "team", "weight": 0.7}}
      ],
      "interests": [
        {{"area": "social_impact", "weight": 0.9}},
        {{"area": "community", "weight": 0.8}}
      ],
      "confidence_impact": 7.0
    }}
  ],
  "context_note": "brief explanation of why this scenario is relevant"
}}

REMEMBER: ABSOLUTELY NO RAISEC-RELATED CONTENT OR FIELDS. Focus exclusively on interests and motivators."""
        
        return prompt
    
    def _validate_and_clean_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the GPT-4 response to remove any RAISEC content"""
        raisec_keywords = [
            'riasec', 'realistic', 'investigative', 'artistic', 
            'social', 'enterprising', 'conventional', 'riasec_weights'
        ]
        
        # Clean option_targets
        if 'option_targets' in response:
            for target in response['option_targets']:
                # Remove any RAISEC fields that might have been included
                for keyword in raisec_keywords:
                    if keyword in target:
                        del target[keyword]
                        logger.warning(f"Removed RAISEC field '{keyword}' from option target")
        
        # Clean the main response
        for keyword in raisec_keywords:
            if keyword in response:
                del response[keyword]
                logger.warning(f"Removed RAISEC field '{keyword}' from main response")
        
        return response
    
    def _analyze_option_targets(self, option_text: str) -> Dict[str, Any]:
        """Analyze option text to determine default target weights for interests and motivators only"""
        
        # Keywords for motivators
        motivator_keywords = {
            'autonomy': ['freedom', 'independent', 'own terms', 'flexible', 'self-directed'],
            'achievement': ['accomplish', 'achieve', 'success', 'results', 'goals'],
            'recognition': ['recognized', 'appreciated', 'reputation', 'respected'],
            'growth': ['learn', 'develop', 'advance', 'progress', 'improve'],
            'stability': ['stable', 'secure', 'predictable', 'consistent'],
            'purpose': ['meaningful', 'impact', 'difference', 'contribute', 'purpose'],
            'creativity': ['creative', 'innovative', 'novel', 'original', 'artistic'],
            'challenge': ['challenging', 'complex', 'difficult', 'demanding'],
            'money': ['financial', 'salary', 'compensation', 'earnings', 'income'],
            'team': ['team', 'collaborate', 'together', 'group', 'collective'],
            'work_life_balance': ['balance', 'family', 'personal time', 'flexibility', 'well-being']
        }
        
        option_lower = option_text.lower()
        
        # Calculate motivator weights
        motivators = []
        for motivator_type, keywords in motivator_keywords.items():
            weight = sum(1 for keyword in keywords if keyword in option_lower) * 0.3
            if weight > 0:
                motivators.append({'type': motivator_type, 'weight': min(weight, 1.0)})
        
        # Default interests based on content
        interests = []
        interest_keywords = {
            'technology': ['tech', 'software', 'digital', 'computer', 'programming', 'coding', 'ai', 'machine learning'],
            'business': ['business', 'startup', 'company', 'enterprise', 'commerce', 'trade'],
            'social_impact': ['social', 'community', 'ngo', 'help', 'volunteer', 'charity', 'non-profit'],
            'arts': ['art', 'creative', 'design', 'painting', 'music', 'dance', 'theater', 'writing'],
            'science': ['science', 'research', 'experiment', 'discover', 'analyze', 'data'],
            'education': ['teach', 'learn', 'education', 'school', 'university', 'knowledge'],
            'healthcare': ['health', 'medical', 'doctor', 'nurse', 'hospital', 'wellness'],
            'sports': ['sports', 'fitness', 'athlete', 'game', 'competition', 'exercise'],
            'environment': ['environment', 'sustainability', 'climate', 'nature', 'eco-friendly'],
            'entertainment': ['entertainment', 'media', 'film', 'tv', 'gaming', 'music']
        }
        
        for interest_area, keywords in interest_keywords.items():
            weight = sum(1 for keyword in keywords if keyword in option_lower) * 0.2
            if weight > 0:
                interests.append({'area': interest_area, 'weight': min(weight, 1.0)})
        
        return {
            'motivators': motivators[:3],  # Top 3 motivators
            'interests': interests[:2],   # Top 2 interests
            'confidence_impact': 5.0      # Default impact
        }
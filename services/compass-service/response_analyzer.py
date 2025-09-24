import json
from typing import List, Dict, Any
from openai import AsyncOpenAI
from compass_schemas import (
    ResponseAnalysis,
    CareerMotivator,
    Interest,
    UserResponse,
    GeneratedQuestion
)

class ResponseAnalyzerService:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.model = "gpt-4-turbo-preview"
        
        self.motivator_types = [
            "Money & Compensation",
            "Growth & Advancement", 
            "Purpose & Impact",
            "Autonomy & Independence",
            "Work-Life Balance",
            "Recognition & Status",
            "Creativity & Innovation",
            "Stability & Security",
            "Learning & Development",
            "Team & Collaboration",
            "Challenge & Competition",
            "Leadership & Influence"
        ]
    
    async def analyze_response(
        self,
        response: UserResponse,
        question: GeneratedQuestion
    ) -> ResponseAnalysis:
        
        if response.skipped:
            return self._create_skipped_analysis()
        
        # Check if this is an MCQ response with metadata
        is_mcq = response.response_text.strip().upper() in ['A', 'B', 'C', 'D']
        
        if is_mcq and question.options:
            # Use the pre-calculated metadata from the selected option
            return self._analyze_mcq_with_metadata(response, question)
        else:
            # Fall back to GPT-4 analysis for free-text responses
            return await self._analyze_with_gpt4(response, question)
    
    def _build_analysis_prompt(self, response_text: str, question_text: str) -> str:
        # Check if this is an MCQ response (single letter A, B, C, or D)
        is_mcq = response_text.strip().upper() in ['A', 'B', 'C', 'D']
        
        if is_mcq:
            prompt = f"""Analyze this MCQ selection for career alignment indicators:

Question and Options: "{question_text}"
User Selected: Option {response_text.strip().upper()}

Based on the option they selected from the scenario, extract signals for:

1. RIASEC Dimensions (rate 0-10 for strength, 0-100 for confidence):
   - Realistic: hands-on, practical, physical activities, tools, outdoors
   - Investigative: analytical, intellectual, research, problem-solving, science
   - Artistic: creative, expressive, innovative, design, unstructured
   - Social: helping, teaching, collaborating, interpersonal, service
   - Enterprising: leading, persuading, business, sales, risk-taking
   - Conventional: organizing, structured, detail-oriented, procedures, data

2. Career Motivators (identify any clearly present):
   {', '.join(self.motivator_types)}

3. Interests: Specific activities, subjects, skills, or domains mentioned

Analyze both explicit statements and implicit indicators. Look for:
- Direct preferences stated
- Emotional language indicating enthusiasm or aversion
- Examples or stories that reveal values
- Problem-solving approaches mentioned
- Work style preferences implied

Output as JSON:
{{
  "riasec": {{
    "realistic": {{"score": 0-10, "confidence": 0-100, "evidence": "quote from response"}},
    "investigative": {{"score": 0-10, "confidence": 0-100, "evidence": "quote"}},
    "artistic": {{"score": 0-10, "confidence": 0-100, "evidence": "quote"}},
    "social": {{"score": 0-10, "confidence": 0-100, "evidence": "quote"}},
    "enterprising": {{"score": 0-10, "confidence": 0-100, "evidence": "quote"}},
    "conventional": {{"score": 0-10, "confidence": 0-100, "evidence": "quote"}}
  }},
  "motivators": [
    {{"type": "motivator name", "strength": 1-10, "evidence": "quote"}}
  ],
  "interests": [
    {{"category": "technology/arts/business/science/etc", "specific": "detailed interest", "enthusiasm": 1-10}}
  ],
  "metadata": {{
    "response_quality": "high/medium/low",
    "contradictions": ["any conflicting signals"],
    "strong_signals": ["notably clear indicators"]
  }}
}}

Be thorough but only include dimensions with actual evidence from the response."""
        else:
            prompt = f"""Analyze this response for career alignment indicators:

Question Asked: "{question_text}"
User Response: "{response_text}"

Extract signals for:

1. RIASEC Dimensions (rate 0-10 for strength, 0-100 for confidence):
   - Realistic: hands-on, practical, physical activities, tools, outdoors
   - Investigative: analytical, intellectual, research, problem-solving, science
   - Artistic: creative, expressive, innovative, design, unstructured
   - Social: helping, teaching, collaborating, interpersonal, service
   - Enterprising: leading, persuading, business, sales, risk-taking
   - Conventional: organizing, structured, detail-oriented, procedures, data

2. Career Motivators (identify any clearly present):
   {', '.join(self.motivator_types)}

3. Interests: Specific activities, subjects, skills, or domains mentioned

Analyze both explicit statements and implicit indicators. Look for:
- Direct preferences stated
- Emotional language indicating enthusiasm or aversion
- Examples or stories that reveal values
- Problem-solving approaches mentioned
- Work style preferences implied

Output as JSON:
{{
  "riasec": {{
    "realistic": {{"score": 0-10, "confidence": 0-100, "evidence": "quote from response"}},
    "investigative": {{"score": 0-10, "confidence": 0-100, "evidence": "quote"}},
    "artistic": {{"score": 0-10, "confidence": 0-100, "evidence": "quote"}},
    "social": {{"score": 0-10, "confidence": 0-100, "evidence": "quote"}},
    "enterprising": {{"score": 0-10, "confidence": 0-100, "evidence": "quote"}},
    "conventional": {{"score": 0-10, "confidence": 0-100, "evidence": "quote"}}
  }},
  "motivators": [
    {{"type": "motivator name", "strength": 1-10, "evidence": "quote"}}
  ],
  "interests": [
    {{"category": "technology/arts/business/science/etc", "specific": "detailed interest", "enthusiasm": 1-10}}
  ],
  "metadata": {{
    "response_quality": "high/medium/low",
    "contradictions": ["any conflicting signals"],
    "strong_signals": ["notably clear indicators"]
  }}
}}

Be thorough but only include dimensions with actual evidence from the response."""
        
        return prompt
    
    def _process_analysis_result(self, result: Dict[str, Any]) -> ResponseAnalysis:
        # Process RIASEC signals
        riasec_signals = {}
        for dimension, data in result.get("riasec", {}).items():
            if data.get("score", 0) > 0:  # Only include dimensions with evidence
                riasec_signals[dimension] = {
                    "score": data.get("score", 0),
                    "confidence": data.get("confidence", 0),
                    "evidence": data.get("evidence", "")
                }
        
        # Process motivators
        motivators = []
        for motivator_data in result.get("motivators", []):
            motivators.append(CareerMotivator(
                type=motivator_data["type"],
                strength=motivator_data["strength"],
                evidence=motivator_data["evidence"],
                confidence=self._calculate_motivator_confidence(motivator_data)
            ))
        
        # Process interests  
        interests = []
        for interest_data in result.get("interests", []):
            interests.append(Interest(
                category=interest_data["category"],
                specific=interest_data["specific"],
                enthusiasm=interest_data["enthusiasm"]
            ))
        
        # Get metadata
        metadata = result.get("metadata", {})
        
        return ResponseAnalysis(
            riasec_signals=riasec_signals,
            motivators=motivators,
            interests=interests,
            response_quality=metadata.get("response_quality", "medium"),
            contradictions=metadata.get("contradictions", []),
            strong_signals=metadata.get("strong_signals", [])
        )
    
    def _calculate_motivator_confidence(self, motivator_data: Dict) -> float:
        # Calculate confidence based on strength and evidence quality
        strength = motivator_data.get("strength", 5)
        has_evidence = bool(motivator_data.get("evidence", "").strip())
        
        if strength >= 8 and has_evidence:
            return 90.0
        elif strength >= 6 and has_evidence:
            return 75.0
        elif strength >= 4 and has_evidence:
            return 60.0
        else:
            return 40.0
    
    def _create_skipped_analysis(self) -> ResponseAnalysis:
        return ResponseAnalysis(
            riasec_signals={},
            motivators=[],
            interests=[],
            response_quality="low",
            contradictions=[],
            strong_signals=[]
        )
    
    def _analyze_mcq_with_metadata(self, response: UserResponse, question: GeneratedQuestion) -> ResponseAnalysis:
        """Extract analysis directly from option metadata"""
        # Find the selected option
        option_letter = response.response_text.strip().upper()
        option_index = ord(option_letter) - ord('A')
        
        if option_index < 0 or option_index >= len(question.options):
            # Invalid option selected
            return self._create_skipped_analysis()
        
        selected_option = question.options[option_index]
        
        # Extract RIASEC signals from option metadata
        riasec_signals = {}
        if selected_option.riasec_weights:
            for dimension, weight in selected_option.riasec_weights.items():
                if weight > 0:
                    riasec_signals[dimension.lower()] = {
                        'score': weight,
                        'confidence': min(weight * 10 + 20, 90),  # Convert weight to confidence
                        'evidence': f"Selected option emphasizing {dimension} traits"
                    }
        
        # Extract motivators from option metadata (list of dicts)
        motivators = []
        if selected_option.motivators:
            for motivator_dict in selected_option.motivators:
                # Handle dict format: {type: "autonomy", weight: 0.7}
                motivator_type = motivator_dict.get('type', 'Unknown')
                motivator_weight = motivator_dict.get('weight', 0.5)
                motivators.append(CareerMotivator(
                    type=motivator_type,
                    strength=motivator_weight * 10,  # Convert 0-1 to 0-10 scale
                    evidence=f"Chose option aligned with {motivator_type}",
                    confidence=motivator_weight * 100  # Convert to percentage
                ))
        
        # Extract interests from option metadata (list of dicts)
        interests = []
        if selected_option.interests:
            for interest_dict in selected_option.interests:
                # Handle dict format: {area: "technology", weight: 0.6}
                interest_area = interest_dict.get('area', 'Unknown')
                interest_weight = interest_dict.get('weight', 0.5)
                interests.append(Interest(
                    category=interest_area,
                    enthusiasm=interest_weight * 10,  # Convert 0-1 to 0-10 scale
                    specific_topics=[interest_area],
                    evidence=f"Selected option related to {interest_area}"
                ))
        
        # Determine strong signals based on highest RIASEC weights
        strong_signals = []
        if riasec_signals:
            sorted_signals = sorted(riasec_signals.items(), key=lambda x: x[1]['score'], reverse=True)
            for dimension, data in sorted_signals[:2]:  # Top 2 signals
                if data['score'] >= 7:
                    strong_signals.append(dimension.capitalize())
        
        return ResponseAnalysis(
            riasec_signals=riasec_signals,
            motivators=motivators,
            interests=interests,
            response_quality="high" if riasec_signals else "medium",
            contradictions=[],
            strong_signals=strong_signals
        )
    
    async def _analyze_with_gpt4(self, response: UserResponse, question: GeneratedQuestion) -> ResponseAnalysis:
        """Fallback to GPT-4 analysis for free-text responses"""
        # Build the analysis prompt
        prompt = self._build_analysis_prompt(response.response_text, question.question_text)
        
        # Get GPT-4 analysis
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert career psychologist analyzing responses for career alignment indicators."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent analysis
            response_format={"type": "json_object"}
        )
        
        result = json.loads(completion.choices[0].message.content)
        
        # Process and structure the analysis
        return self._process_analysis_result(result)
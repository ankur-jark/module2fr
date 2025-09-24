export interface JourneyState {
  journey_id: string
  user_id: string
  status: 'not_started' | 'in_progress' | 'completed' | 'abandoned'
  demographics?: any
  preferences?: any
  current_question_number: number
  current_question?: Question
  current_profile?: RIASECProfile
  current_confidence?: ConfidenceScore
  identified_motivators?: Motivator[]
  identified_interests?: Interest[]
  last_decision?: Decision
  questions_asked: Question[]
  responses: Response[]
}

export interface OptionTarget {
  id: string
  text: string
  riasec_weights: {
    realistic?: number
    investigative?: number
    artistic?: number
    social?: number
    enterprising?: number
    conventional?: number
  }
  motivators: Array<{
    type: string
    weight: number
  }>
  interests: Array<{
    area: string
    weight: number
  }>
  confidence_impact: number
}

export interface Question {
  question_id: string
  question_number: number
  question_text: string
  options: OptionTarget[]  // New field for structured options with metadata
  target_dimensions?: {
    primary?: string
    secondary?: string[]
  }
  context_note?: string
}

export interface RIASECProfile {
  realistic: number
  investigative: number
  artistic: number
  social: number
  enterprising: number
  conventional: number
}

export interface ConfidenceScore {
  overall_confidence: number
  riasec_confidence: {
    realistic: number
    investigative: number
    artistic: number
    social: number
    enterprising: number
    conventional: number
  }
  motivator_confidence: number
  interest_confidence: number
  ready_to_complete: boolean
  gaps_remaining: string[]
}

export interface Motivator {
  type: string
  strength: number
  evidence: string
  confidence: number
}

export interface Interest {
  category: string
  specific: string
  enthusiasm: number
}

export interface Decision {
  decision: 'continue' | 'clarify' | 'complete' | 'save_partial'
  reasoning: string
  next_focus?: string
}

export interface Response {
  question_id: string
  response_text: string
  response_time_seconds: number
  skipped: boolean
}

export interface Event {
  type: string
  message: string
  timestamp?: Date
  data?: any
}
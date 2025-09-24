'use client'

import { useState, useEffect } from 'react'
import { Send, SkipForward } from 'lucide-react'
import axios from 'axios'
import { JourneyState, Event, OptionTarget } from '@/types/journey'
import OptionDisplay from './OptionDisplay'

interface Props {
  journeyState: JourneyState | null
  onJourneyUpdate: (state: JourneyState) => void
  onEvent: (event: Event) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export default function ResponseInput({ 
  journeyState, 
  onJourneyUpdate, 
  onEvent,
  isLoading,
  setIsLoading 
}: Props) {
  const [selectedOption, setSelectedOption] = useState<string>('')
  const [responseTime, setResponseTime] = useState(0)
  const [timer, setTimer] = useState<NodeJS.Timeout | null>(null)

  // Start timer when question appears
  const startTimer = () => {
    const start = Date.now()
    const t = setInterval(() => {
      setResponseTime(Math.floor((Date.now() - start) / 1000))
    }, 1000)
    setTimer(t)
  }

  // Stop timer
  const stopTimer = () => {
    if (timer) {
      clearInterval(timer)
      setTimer(null)
    }
  }

  const submitResponse = async (skipped: boolean = false) => {
    if (!journeyState?.journey_id || !journeyState?.current_question) return
    
    stopTimer()
    setIsLoading(true)
    
    try {
      const response = await axios.post(
        `http://localhost:8000/api/v1/compass/journey/${journeyState.journey_id}/response`,
        {
          question_id: journeyState.current_question.question_id,
          response_text: skipped ? '' : selectedOption,
          response_time_seconds: responseTime,
          skipped
        }
      )
      
      const decision = response.data
      
      onEvent({
        type: 'response_submitted',
        message: `Response submitted: ${skipped ? 'SKIPPED' : selectedOption} (${responseTime}s)`,
        data: decision
      })
      
      // Get updated journey state
      const journeyResponse = await axios.get(
        `http://localhost:8000/api/v1/compass/journey/${journeyState.journey_id}`
      )
      
      onJourneyUpdate(journeyResponse.data)
      
      // Check decision and get next question if continuing
      if (decision.decision === 'continue' || decision.decision === 'clarify') {
        const nextQuestion = await axios.post(
          `http://localhost:8000/api/v1/compass/journey/${journeyState.journey_id}/next-question`
        )
        
        const updatedJourney = await axios.get(
          `http://localhost:8000/api/v1/compass/journey/${journeyState.journey_id}`
        )
        
        onJourneyUpdate({
          ...updatedJourney.data,
          current_question: nextQuestion.data,
          last_decision: decision
        })
        
        // Reset for next question
        setSelectedOption('')
        setResponseTime(0)
        startTimer()
      } else if (decision.decision === 'complete') {
        onEvent({
          type: 'journey_completed',
          message: 'Journey completed!'
        })
      }
    } catch (error) {
      console.error('Failed to submit response:', error)
      onEvent({
        type: 'error',
        message: 'Failed to submit response'
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Start timer when new question appears
  useEffect(() => {
    if (journeyState?.current_question) {
      setResponseTime(0)
      startTimer()
    }
    return () => stopTimer()
  }, [journeyState?.current_question?.question_id])

  // Get question and options
  const getQuestionData = () => {
    if (!journeyState?.current_question) return { question: '', options: [] }
    
    // Use structured options if available
    if (journeyState.current_question.options && journeyState.current_question.options.length > 0) {
      // Extract clean question text (without embedded options)
      const text = journeyState.current_question.question_text
      const firstOptionIndex = text.indexOf('A)')
      const questionText = firstOptionIndex > -1 ? text.substring(0, firstOptionIndex).trim() : text
      
      return {
        question: questionText,
        options: journeyState.current_question.options
      }
    }
    
    // Fallback: Parse options from text if structured options not available
    const text = journeyState.current_question.question_text
    const firstOptionIndex = text.indexOf('A)')
    const questionText = firstOptionIndex > -1 ? text.substring(0, firstOptionIndex).trim() : text
    
    const options: OptionTarget[] = []
    if (firstOptionIndex > -1) {
      const patterns = ['A)', 'B)', 'C)', 'D)']
      for (let i = 0; i < patterns.length; i++) {
        const start = text.indexOf(patterns[i])
        if (start === -1) break
        
        const nextPattern = i < patterns.length - 1 ? patterns[i + 1] : null
        const end = nextPattern ? text.indexOf(nextPattern) : text.length
        
        if (end > start) {
          const optionText = text.substring(start + 3, end).trim()
          // Create basic option without metadata when parsing from text
          options.push({
            id: patterns[i].replace(')', ''),
            text: optionText,
            riasec_weights: {},
            motivators: [],
            interests: [],
            confidence_impact: 0
          })
        }
      }
    }
    
    return { question: questionText, options }
  }

  const { question, options } = getQuestionData()
  const hasMetadata = options.some(opt => 
    (opt.motivators && opt.motivators.length > 0) ||
    (opt.interests && opt.interests.length > 0)
  )

  if (!journeyState?.current_question) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Response Input</h2>
        <p className="text-sm text-gray-500">Start a journey to answer questions</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Response Input</h2>
        <span className="text-sm text-gray-500">Time: {responseTime}s</span>
      </div>

      {options.length > 0 ? (
        <div className="space-y-4">
          {/* Show metadata if available */}
          {hasMetadata && (
            <div className="text-xs text-gray-500 bg-gray-50 rounded-lg p-3 mb-4">
              <span className="font-semibold">💡 Tip:</span> Each option reveals different aspects of your personality, interests, and motivators. The metadata below each option shows what it measures.
            </div>
          )}
          
          {options.map((option) => (
            hasMetadata ? (
              <OptionDisplay
                key={option.id}
                option={option}
                isSelected={selectedOption === option.id}
                onSelect={() => setSelectedOption(option.id)}
                disabled={isLoading}
              />
            ) : (
              // Fallback to simple display if no metadata
              <button
                key={option.id}
                onClick={() => setSelectedOption(option.id)}
                disabled={isLoading}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                  selectedOption === option.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                } disabled:opacity-50`}
              >
                <span className="font-semibold mr-2">{option.id})</span>
                <span className="text-sm">{option.text}</span>
              </button>
            )
          ))}
        </div>
      ) : (
        <textarea
          value={selectedOption}
          onChange={(e) => setSelectedOption(e.target.value)}
          placeholder="Type your response here..."
          className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg resize-none"
          disabled={isLoading}
        />
      )}

      <div className="flex gap-2 mt-4">
        <button
          onClick={() => submitResponse(false)}
          disabled={isLoading || !selectedOption}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          Submit
        </button>
        
        <button
          onClick={() => submitResponse(true)}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50"
        >
          <SkipForward className="w-4 h-4" />
          Skip
        </button>
      </div>
    </div>
  )
}
'use client'

import { useState, useEffect } from 'react'
import OptionDisplay from '@/components/OptionDisplay'
import { ChevronRight, ChevronLeft, Info } from 'lucide-react'
import { mockQuestionsWithMetadata } from '@/utils/raisecQB'
import { useRouter } from 'next/navigation'

// Define the response interface
interface UserResponse {
  session_id: string;
  question_id: string;
  question_number: number;
  option_index: number;
  option_id: string;
  timestamp: number;
  metadata?: any; //You can store additional metadata here
}

// Generate a unique session ID
function generateSessionId(): string {
  return 'session_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
}

export default function DemoPage() {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [sessionId, setSessionId] = useState<string>('')
  const [userResponses, setUserResponses] = useState<UserResponse[]>([])
  const [finalResult, setFinalResult] = useState<any>(null)
  const [fetchError, setFetchError] = useState<string|null>(null)
  const router = useRouter()
  
  const currentQuestion = mockQuestionsWithMetadata[currentQuestionIndex]
  
  // Get selected option for current question
  const currentResponse = userResponses.find(
    response => response.question_id === currentQuestion.question_id
  )
  const selectedOption = currentResponse?.option_id || ''

  // Initialize session ID on component mount
  useEffect(() => {
    const newSessionId = generateSessionId()
    setSessionId(newSessionId)
    console.log('New session started:', newSessionId)
  }, [])

  // Persist final result and then redirect to Module 2
  useEffect(() => {
    if (finalResult) {
      try {
        const payload = {
          data: finalResult,
          storedAt: Date.now(),
          sessionId,
        }
        // Store in localStorage so it survives tab reloads. Switch to sessionStorage if you want per-tab lifetime.
        localStorage.setItem('module2FinalResult', JSON.stringify(payload))

        // Additionally store parsed Update Profile payload for later use
        try {
          const c = finalResult?.confidence_score || finalResult?.data?.confidence_score
          if (c?.riasec_confidence) {
            const current_profile = {
              realistic: Math.round(c.riasec_confidence.realistic * 100),
              investigative: Math.round(c.riasec_confidence.investigative * 100),
              artistic: Math.round(c.riasec_confidence.artistic * 100),
              social: Math.round(c.riasec_confidence.social * 100),
              enterprising: Math.round(c.riasec_confidence.enterprising * 100),
              conventional: Math.round(c.riasec_confidence.conventional * 100),
            }
            const updatePayload = {
              current_profile,
              reason: 'Automated update from Module 2 final results',
            }
            localStorage.setItem('module2UpdateProfilePayload', JSON.stringify(updatePayload))
          }
        } catch (ignored) {}

        // Also store as a cookie so it can be read across ports (cookies are domain-scoped, not port-scoped)
        // Keep it short-lived to avoid stale data
        const encoded = encodeURIComponent(JSON.stringify(payload))
        // 10 minutes expiry
        const maxAge = 10 * 60
        document.cookie = `module2FinalResult=${encoded}; Max-Age=${maxAge}; Path=/; SameSite=Lax`;
      } catch (e) {
        console.error('Failed to persist final result', e)
      }

      // Navigate to assessment page to start module 2
      router.push('/assessment')
    }
  }, [finalResult, sessionId])

  const handleSelectOption = (optionId: string) => {
    const optionIndex = currentQuestion.options.findIndex(opt => opt.id === optionId)
    // Guard: if option not found, do nothing to avoid invalid array access
    if (optionIndex < 0) return
    
    const newResponse: UserResponse = {
      session_id: sessionId,
      question_id: currentQuestion.question_id,
      question_number: currentQuestion.question_number,
      option_index: optionIndex,
      option_id: optionId,
      timestamp: Date.now(),
      metadata: {
        // You can store additional metadata from the option if needed
        riasec_weights: currentQuestion.options[optionIndex].riasec_weights,
        motivators: currentQuestion.options[optionIndex].motivators,
        interests: currentQuestion.options[optionIndex].interests,
        confidence_impact: currentQuestion.options[optionIndex].confidence_impact
      }
    }

    setUserResponses(prev => {
      // Remove existing response for this question if it exists
      const filtered = prev.filter(response => response.question_id !== currentQuestion.question_id)
      // Add new response
      return [...filtered, newResponse]
    })
  }

  const handleNextQuestion = () => {
    if (currentQuestionIndex < mockQuestionsWithMetadata.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
    } else {
      // All questions completed - ready to send data
      handleCompletion()
    }
  }

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1)
    }
  }

  const handleCompletion = async () => {
    console.log('All questions completed! User responses:', userResponses)

    // Prepare submissionData as before
    const submissionData = {
      session_id: sessionId,
      started_at: userResponses[0]?.timestamp || Date.now(),
      completed_at: Date.now(),
      total_questions: mockQuestionsWithMetadata.length,
      responses: userResponses,
      summary: generateSummary(userResponses)
    }

    console.log('Data ready for backend:', submissionData)

    try {
      const response = await fetch('http://localhost:8004/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(submissionData),
      })

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`)
      }

      const data = await response.json()
      console.log('Server response:', data)
      setFinalResult(data)
      setFetchError(null)
    } catch (error: any) {
      console.error('Error fetching score:', error)
      setFetchError(error.message)
      setFinalResult(null)
    }
  }

  // Helper function to generate a summary of responses
  const generateSummary = (responses: UserResponse[]) => {
    // Calculate average RIASEC scores, etc.
    return {
      total_responses: responses.length,
      // Add any summary metrics you need
    }
  }

  const isLastQuestion = currentQuestionIndex === mockQuestionsWithMetadata.length - 1

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 sm:p-6 lg:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6 sm:mb-8 text-center">
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
            TruScholar Compass Demo
          </h1>
          <p className="text-gray-600 text-sm sm:text-base">
            Experience how each option reveals your personality, interests, and motivators
          </p>
          <div className="mt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
            <span className="text-sm text-gray-500">
              Question {currentQuestionIndex + 1} of {mockQuestionsWithMetadata.length}
            </span>
            <div className="w-48 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentQuestionIndex + 1) / mockQuestionsWithMetadata.length) * 100}%` }}
              />
            </div>
          </div>
          {/* Session ID Display */}
          <div className="mt-2">
            <span className="text-xs text-gray-400">Session: {sessionId}</span>
          </div>
        </div>

        {/* Response Status */}
        <div className="mb-4 text-center">
          <span className="text-sm text-green-600">
            Responses recorded: {userResponses.length}/{mockQuestionsWithMetadata.length}
          </span>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-xl sm:rounded-2xl shadow-lg sm:shadow-xl p-4 sm:p-6 lg:p-8 mb-6 sm:mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2 sm:px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs sm:text-sm font-semibold">
                Question #{currentQuestion.question_number}
              </span>
              <span className="text-gray-500 text-xs sm:text-sm">{currentQuestion.context_note}</span>
            </div>
            <span className="text-xs text-gray-400 self-end sm:self-auto">{currentQuestion.question_id}</span>
          </div>

          <h2 className="text-xl sm:text-2xl font-semibold text-gray-800 mb-4 sm:mb-6 leading-relaxed">
            {currentQuestion.question_text}
          </h2>

          {/* Info Box */}
          <div className="flex items-start gap-3 p-3 sm:p-4 bg-blue-50 border border-blue-200 rounded-lg mb-4 sm:mb-6">
            <Info className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-xs sm:text-sm text-blue-800">
              <p className="font-semibold mb-1">How this works:</p>
              <ul className="space-y-1 list-disc list-inside">
                <li>Each option measures different RIASEC dimensions (personality traits)</li>
                <li>Motivators show what drives you in your career</li>
                <li>Interests indicate areas you're naturally drawn to</li>
                <li>Confidence impact shows how much clarity this brings to your profile</li>
              </ul>
            </div>
          </div>

          {/* Options Display */}
          <div className="space-y-4 sm:space-y-6">
            {currentQuestion.options.map((option, index) => (
              <OptionDisplay
                key={option.id}
                option={option}
                isSelected={selectedOption === option.id}
                onSelect={() => handleSelectOption(option.id)}
                disabled={false}
                optionIndex={index} // Pass the index for display if needed
              />
            ))}
          </div>

          {/* Navigation Buttons */}
          <div className="mt-6 sm:mt-8 flex flex-col-reverse sm:flex-row justify-between items-center gap-4">
            <button
              onClick={handlePreviousQuestion}
              disabled={currentQuestionIndex === 0}
              className="flex items-center gap-2 px-4 sm:px-6 py-2 sm:py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all w-full sm:w-auto justify-center"
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </button>

            <button
              onClick={handleNextQuestion}
              disabled={!selectedOption}
              className="flex items-center gap-2 px-4 sm:px-8 py-2 sm:py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105 w-full sm:w-auto justify-center"
            >
              {isLastQuestion ? 'Complete Assessment' : 'Next Question'}
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Debug Panel (remove in production) */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-yellow-800 mb-2">Debug Info</h3>
          <div className="text-xs text-yellow-700">
            <p><strong>Session ID:</strong> {sessionId}</p>
            <p><strong>Current Question:</strong> {currentQuestion.question_id}</p>
            <p><strong>Responses:</strong> {userResponses.length}</p>
            <details>
              <summary className="cursor-pointer">View Response Data</summary>
              <pre className="mt-2 whitespace-pre-wrap">{JSON.stringify(userResponses, null, 2)}</pre>
            </details>
          </div>
        </div>

        {/* Final Result and Error Display */}
        {finalResult && (
          <div className="mb-6 p-4 border rounded-lg bg-white">
            <h3 className="font-semibold mb-2">Final Result (JSON):</h3>
            <pre className="whitespace-pre-wrap">{JSON.stringify(finalResult, null, 2)}</pre>
          </div>
        )}

        {fetchError && (
          <div className="mb-6 p-4 border rounded-lg bg-red-50 text-red-700">
            <strong>Error:</strong> {fetchError}
          </div>
        )}

        {/* Legend */}
        <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6">
          <h3 className="text-lg font-semibold mb-3 sm:mb-4">Understanding the Metadata</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
            <div>
              <h4 className="font-semibold text-gray-700 mb-2 text-sm sm:text-base">RIASEC Dimensions</h4>
              <ul className="space-y-1 text-xs sm:text-sm text-gray-600">
                <li><span className="font-medium">R</span> - Realistic: Hands-on, practical</li>
                <li><span className="font-medium">I</span> - Investigative: Analytical, research</li>
                <li><span className="font-medium">A</span> - Artistic: Creative, expressive</li>
                <li><span className="font-medium">S</span> - Social: Helping, collaborative</li>
                <li><span className="font-medium">E</span> - Enterprising: Leadership, business</li>
                <li><span className="font-medium">C</span> - Conventional: Organized, structured</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-gray-700 mb-2 text-sm sm:text-base">Career Motivators</h4>
              <p className="text-xs sm:text-sm text-gray-600">
                Shows what drives you: autonomy, growth, purpose, stability, creativity, 
                recognition, team collaboration, challenges, and more.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-gray-700 mb-2 text-sm sm:text-base">Interest Areas</h4>
              <p className="text-xs sm:text-sm text-gray-600">
                Indicates specific fields and activities you're naturally drawn to, 
                helping identify potential career paths.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
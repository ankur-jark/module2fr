'use client'

import { useState, useEffect } from 'react'

interface RIASECProfile {
  realistic: number;
  investigative: number;
  artistic: number;
  social: number;
  enterprising: number;
  conventional: number;
}

interface RIASECConfidence {
  realistic: number;
  investigative: number;
  artistic: number;
  social: number;
  enterprising: number;
  conventional: number;
}

interface ConfidenceData {
  riasec_confidence: RIASECConfidence;
  overall_confidence: number;
  ready_to_complete: boolean;
  motivator_confidence: number;
  interest_confidence: number;
  gaps_remaining: string[];
}

interface UpdateProfileRequest {
  current_profile: RIASECProfile;
  reason: string;
}

interface Module2FinalResult {
  data: {
    confidence_score: {
      riasec_confidence: RIASECConfidence;
      overall_confidence: number;
      ready_to_complete: boolean;
    };
    // ... other fields if needed
  };
}

export default function ProfileUpdater() {
  const [journeyId, setJourneyId] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [parsedData, setParsedData] = useState<UpdateProfileRequest | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState<any | null>(null)

  // Helpers
  const getCookie = (name: string): string | null => {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop()!.split(';').shift() || null
    return null
  }

  // Parse module2FinalResult from cookie (cross-port) then localStorage fallback
  const parseModule2Data = (): UpdateProfileRequest | null => {
    try {
      // Try cookie first
      const cookieVal = getCookie('module2FinalResult')
      const storedData = cookieVal ? decodeURIComponent(cookieVal) : localStorage.getItem('module2FinalResult')
      if (!storedData) {
        setMessage('No module2FinalResult found (cookie or localStorage)')
        return null
      }

      const module2Data: Module2FinalResult = JSON.parse(storedData)
      const confidenceData = module2Data.data.confidence_score

      // Convert decimal confidence scores to percentages (0-100 scale)
      const riasecProfile: RIASECProfile = {
        realistic: Math.round(confidenceData.riasec_confidence.realistic * 100),
        investigative: Math.round(confidenceData.riasec_confidence.investigative * 100),
        artistic: Math.round(confidenceData.riasec_confidence.artistic * 100),
        social: Math.round(confidenceData.riasec_confidence.social * 100),
        enterprising: Math.round(confidenceData.riasec_confidence.enterprising * 100),
        conventional: Math.round(confidenceData.riasec_confidence.conventional * 100)
      }

      // Omit current_confidence from the payload per API requirement
      return {
        current_profile: riasecProfile,
        reason: "Automated update from Module 2 final results"
      }
    } catch (error) {
      setMessage('Error parsing module2FinalResult: ' + error)
      return null
    }
  }

  const updateProfile = async (profileData: UpdateProfileRequest) => {
    if (!journeyId) {
      setMessage('Please enter a journey ID')
      return
    }

    setIsLoading(true)
    setMessage('')

    try {
      const response = await fetch(`http://localhost:8000/api/v1/compass/journey/${journeyId}/update-profile`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify(profileData)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      setMessage('Profile updated successfully!')
      console.log('Update response:', result)
      // Immediately trigger first question generation
      await generateFirstQuestion(journeyId)
      
    } catch (error) {
      setMessage('Error updating profile: ' + error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateFirstQuestion = async (jId: string) => {
    try {
      // Ask backend to generate next (first) question
      const qRes = await fetch(`http://localhost:8000/api/v1/compass/journey/${jId}/next-question`, {
        method: 'POST'
      })
      if (!qRes.ok) throw new Error(`next-question failed: ${qRes.status}`)
      const question = await qRes.json()

      // Get latest journey state
      const stateRes = await fetch(`http://localhost:8000/api/v1/compass/journey/${jId}`)
      if (!stateRes.ok) throw new Error(`get journey failed: ${stateRes.status}`)
      const journeyState = await stateRes.json()

      setCurrentQuestion(question)
      setMessage(`First question generated (Q#${question.question_number}). Ready to answer.`)
      console.log('Journey state after question:', journeyState)
    } catch (err) {
      console.error('Failed to generate first question:', err)
      setMessage('Failed to generate first question: ' + err)
    }
  }

  const handleParseData = () => {
    const data = parseModule2Data()
    if (data) {
      setParsedData(data)
      setMessage('Data parsed successfully! Ready to update.')
    }
  }

  const handleUpdate = () => {
    if (parsedData) {
      updateProfile(parsedData)
    }
  }

  // Start Journey with mock payload and set journeyId from response
  const startJourney = async () => {
    setIsLoading(true)
    setMessage('')
    try {
      const body = {
        user_id: 'user_123',
        demographics: {
          age: 22,
          education_level: 'bachelor',
          current_status: 'student',
          location: 'San Francisco, CA'
        },
        preferences: {
          language: 'en',
          question_style: 'casual',
          time_available: '15-20 minutes'
        }
      }

      const res = await fetch('http://localhost:8000/api/v1/compass/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }

      const json = await res.json()
      if (json?.journey_id) {
        setJourneyId(json.journey_id)
        setMessage('Journey started successfully. Journey ID populated.')
      } else {
        setMessage('Journey started, but no journey_id found in response')
      }
    } catch (err) {
      setMessage('Error starting journey: ' + err)
    } finally {
      setIsLoading(false)
    }
  }

  // Auto-parse data when component mounts
  useEffect(() => {
    handleParseData()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">
            Update Journey Profile from Module 2 Results
          </h1>

          {/* Journey ID Input */}
          <div className="mb-6">
            <label htmlFor="journeyId" className="block text-sm font-medium text-gray-700 mb-2">
              Journey ID
            </label>
            <input
              type="text"
              id="journeyId"
              value={journeyId}
              onChange={(e) => setJourneyId(e.target.value)}
              placeholder="Enter journey ID from /compass/start response"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4 mb-6">
            <button
              onClick={startJourney}
              disabled={isLoading}
              className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Starting…' : 'Start Journey (mock)'}
            </button>
            
            <button
              onClick={handleParseData}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Parse Module 2 Data
            </button>
            
            <button
              onClick={handleUpdate}
              disabled={!parsedData || !journeyId || isLoading}
              className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Updating...' : 'Update Profile'}
            </button>
          </div>

          {/* Message Display */}
          {message && (
            <div className={`p-3 rounded-md mb-6 ${
              message.includes('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
            }`}>
              {message}
            </div>
          )}

          {/* Parsed Data Preview */}
          {parsedData && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Parsed Data Preview</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <pre className="text-sm overflow-auto max-h-64">
                  {JSON.stringify(parsedData, null, 2)}
                </pre>
              </div>
              
              {/* RIASEC Profile Summary */}
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-700">RIASEC Scores (0-100)</h4>
                  <ul className="text-sm text-gray-600 mt-2">
                    {Object.entries(parsedData.current_profile).map(([key, value]) => (
                      <li key={key} className="flex justify-between">
                        <span className="capitalize">{key}:</span>
                        <span>{value}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                {/* After update, preview the first question if available */}
                {currentQuestion && (
                  <div className="bg-white rounded border p-3">
                    <h4 className="font-medium text-gray-700 mb-2">First Question</h4>
                    <div className="text-sm text-gray-800">
                      <div className="mb-1">Question #{currentQuestion.question_number}</div>
                      <div>{currentQuestion.question_text}</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
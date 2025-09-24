'use client'

import { useState } from 'react'
import { Play, Pause, RotateCcw, StopCircle } from 'lucide-react'
import axios from 'axios'
import { JourneyState, Event } from '@/types/journey'

interface Props {
  onJourneyUpdate: (state: JourneyState) => void
  onEvent: (event: Event) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
  currentJourneyState?: JourneyState
}

export default function JourneyControl({ 
  onJourneyUpdate, 
  onEvent,
  isLoading,
  setIsLoading,
  currentJourneyState
}: Props) {
  const [journeyId, setJourneyId] = useState<string>('')
  const [userId] = useState(`test_user_${Date.now()}`)
  const [age, setAge] = useState(25)
  
  const startJourney = async () => {
    setIsLoading(true)
    try {
      const response = await axios.post('http://localhost:8000/api/v1/compass/start', {
        user_id: userId,
        demographics: {
          age,
          education_level: 'bachelor',
          current_status: 'working'
        },
        preferences: {
          language: 'en',
          question_style: 'casual'
        }
      })
      
      const journeyData = response.data
      setJourneyId(journeyData.journey_id)
      onJourneyUpdate(journeyData)
      onEvent({
        type: 'journey_started',
        message: `Journey started with ID: ${journeyData.journey_id}`
      })
      
      // Get first question
      await getNextQuestion(journeyData.journey_id)
    } catch (error) {
      console.error('Failed to start journey:', error)
      onEvent({
        type: 'error',
        message: 'Failed to start journey'
      })
    } finally {
      setIsLoading(false)
    }
  }
  
  const getNextQuestion = async (jId: string) => {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/v1/compass/journey/${jId}/next-question`
      )
      
      const journeyResponse = await axios.get(
        `http://localhost:8000/api/v1/compass/journey/${jId}`
      )
      
      onJourneyUpdate({
        ...journeyResponse.data,
        current_question: response.data
      })
      
      onEvent({
        type: 'question_generated',
        message: `Question #${response.data.question_number} generated`
      })
    } catch (error) {
      console.error('Failed to get next question:', error)
    }
  }
  
  const updateProfileFromLocal = async () => {
    if (!journeyId) {
      onEvent({
        type: 'error',
        message: 'No journey started. Start a journey first.'
      })
      return
    }
    try {
      setIsLoading(true)
      const stored = localStorage.getItem('module2UpdateProfilePayload')
      if (!stored) {
        onEvent({
          type: 'error',
          message: 'No module2UpdateProfilePayload found in localStorage'
        })
        return
      }
      const payload = JSON.parse(stored)
      const res = await fetch(`http://localhost:8000/api/v1/compass/journey/${journeyId}/update-profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }
      // Refetch journey to update UI with latest RIASEC metrics
      try {
        const refreshed = await fetch(`http://localhost:8000/api/v1/compass/journey/${journeyId}`)
        if (!refreshed.ok) throw new Error(`HTTP ${refreshed.status}`)
        const refreshedState = await refreshed.json()
        onJourneyUpdate({
          ...refreshedState,
          // Preserve the active question in UI so the loop isn't interrupted
          current_question: currentJourneyState?.current_question,
          current_question_number: currentJourneyState?.current_question_number ?? refreshedState.current_question_number
        })
      } catch (refreshErr) {
        console.error('Failed to refresh journey after profile update:', refreshErr)
      }
      onEvent({
        type: 'profile_updated',
        message: 'Profile updated from Module 2 payload'
      })
    } catch (error) {
      console.error('Failed to update profile:', error)
      onEvent({
        type: 'error',
        message: 'Failed to update profile'
      })
    } finally {
      setIsLoading(false)
    }
  }
  
  const abandonJourney = async () => {
    if (!journeyId) return
    
    try {
      await axios.post(`http://localhost:8000/api/v1/compass/journey/${journeyId}/abandon`)
      onEvent({
        type: 'journey_abandoned',
        message: 'Journey abandoned'
      })
      setJourneyId('')
    } catch (error) {
      console.error('Failed to abandon journey:', error)
    }
  }
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Journey Control</h2>
      
      <div className="space-y-4">
        {/* User Settings */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            User Age
          </label>
          <input
            type="number"
            value={age}
            onChange={(e) => setAge(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            min="16"
            max="80"
          />
        </div>
        
        {/* Control Buttons */}
        <div className="flex gap-2">
          <button
            onClick={startJourney}
            disabled={isLoading || !!journeyId}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            <Play className="w-4 h-4" />
            Start
          </button>
          
          <button
            onClick={updateProfileFromLocal}
            disabled={isLoading || !journeyId}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RotateCcw className="w-4 h-4" />
            Update Profile
          </button>
          
          <button
            onClick={abandonJourney}
            disabled={!journeyId}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            <StopCircle className="w-4 h-4" />
            Stop
          </button>
        </div>
        
        {/* Journey Info */}
        {journeyId && (
          <div className="pt-4 border-t">
            <p className="text-sm text-gray-600">
              <span className="font-medium">Journey ID:</span>
              <br />
              <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                {journeyId}
              </code>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
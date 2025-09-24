'use client'

import { useState } from 'react'
import JourneyControl from '@/components/JourneyControl'
import PromptDisplay from '@/components/PromptDisplay'
import RIASECTracker from '@/components/RIASECTracker'
import MotivatorsTracker from '@/components/MotivatorsTracker'
import InterestsDisplay from '@/components/InterestsDisplay'
import ConfidenceMeter from '@/components/ConfidenceMeter'
import DecisionDisplay from '@/components/DecisionDisplay'
import JourneyFlow from '@/components/JourneyFlow'
import ResponseInput from '@/components/ResponseInput'
import EventLog from '@/components/EventLog'
import { JourneyState, Event } from '@/types/journey'

export default function AssessmentRunner() {
  const [journeyState, setJourneyState] = useState<JourneyState | null>(null)
  const [events, setEvents] = useState<Event[]>([])
  const [currentPrompt, setCurrentPrompt] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const addEvent = (event: Event) => {
    setEvents(prev => [...prev, { ...event, timestamp: new Date() }])
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Compass Assessment Module 2
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Start or resume a journey, answer questions, and continue the loop
          </p>
        </div>
      </header>

      {/* Main Layout */}
      <div className="p-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Panel - Journey Control & Flow */}
          <div className="col-span-3 space-y-6">
            <JourneyControl 
              onJourneyUpdate={setJourneyState}
              onEvent={addEvent}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
              currentJourneyState={journeyState || undefined}
            />

            <JourneyFlow 
              journeyState={journeyState}
              currentStep={journeyState?.current_question_number || 0}
            />
          </div>

          {/* Center Panel - Main Interaction */}
          <div className="col-span-6 space-y-6">
            {/* Current Question & Response */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Current Interaction</h2>
              {journeyState?.current_question && (
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-600 font-medium mb-1">
                      Question #{journeyState.current_question_number}
                    </p>
                    <p className="text-gray-900">
                      {journeyState.current_question.question_text.split('A)')[0].trim()}
                    </p>
                  </div>

                  <ResponseInput
                    journeyState={journeyState}
                    onJourneyUpdate={setJourneyState}
                    onEvent={addEvent}
                    isLoading={isLoading}
                    setIsLoading={setIsLoading}
                  />
                </div>
                
              )}
            </div>

            {/* Prompts Display */}
            <PromptDisplay 
              currentPrompt={currentPrompt}
              journeyState={journeyState}
            />

            {/* Decision Engine */}
            <DecisionDisplay 
              decision={journeyState?.last_decision}
              confidence={journeyState?.current_confidence}
            />
          </div>

          {/* Right Panel - Trackers & Metrics */}
          <div className="col-span-3 space-y-6">
            {/* Confidence Meters */}
            <ConfidenceMeter 
              confidence={journeyState?.current_confidence}
            />

            {/* RIASEC Tracker */}
            <RIASECTracker 
              scores={journeyState?.current_profile}
            />

            {/* Motivators */}
            <MotivatorsTracker 
              motivators={journeyState?.identified_motivators || []}
            />

            {/* Interests */}
            <InterestsDisplay 
              interests={journeyState?.identified_interests || []}
            />
          </div>
        </div>

        {/* Bottom Panel - Event Log */}
        <div className="mt-6">
          <EventLog events={events} />
        </div>
      </div>
    </div>
  )
}



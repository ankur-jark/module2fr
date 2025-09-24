'use client'

import { CheckCircle, Circle, Lock } from 'lucide-react'
import { JourneyState } from '@/types/journey'

interface Props {
  journeyState: JourneyState | null
  currentStep: number
}

export default function JourneyFlow({ journeyState, currentStep }: Props) {
  const steps = [
    { id: 1, name: 'Initialize', status: currentStep > 0 ? 'complete' : currentStep === 0 ? 'current' : 'upcoming' },
    { id: 2, name: 'Build Context', status: currentStep > 1 ? 'complete' : currentStep === 1 ? 'current' : 'upcoming' },
    { id: 3, name: 'Questions 1-5', status: currentStep > 5 ? 'complete' : currentStep >= 1 && currentStep <= 5 ? 'current' : 'upcoming' },
    { id: 4, name: 'Questions 6-10', status: currentStep > 10 ? 'complete' : currentStep >= 6 && currentStep <= 10 ? 'current' : 'upcoming' },
    { id: 5, name: 'Questions 11-15', status: currentStep > 15 ? 'complete' : currentStep >= 11 && currentStep <= 15 ? 'current' : 'upcoming' },
    { id: 6, name: 'Clarifications', status: currentStep > 18 ? 'complete' : currentStep >= 16 && currentStep <= 18 ? 'current' : 'upcoming' },
    { id: 7, name: 'Synthesize', status: journeyState?.status === 'completed' ? 'complete' : 'upcoming' },
    { id: 8, name: 'Deliver', status: journeyState?.status === 'completed' ? 'complete' : 'upcoming' },
  ]

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Journey Flow</h2>
      
      <div className="space-y-3">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center gap-3">
            <div className="flex-shrink-0">
              {step.status === 'complete' ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : step.status === 'current' ? (
                <div className="w-5 h-5 rounded-full border-2 border-blue-600 bg-blue-100 animate-pulse" />
              ) : (
                <Circle className="w-5 h-5 text-gray-300" />
              )}
            </div>
            
            <div className="flex-grow">
              <p className={`text-sm font-medium ${
                step.status === 'current' ? 'text-blue-600' : 
                step.status === 'complete' ? 'text-green-600' : 
                'text-gray-400'
              }`}>
                {step.name}
              </p>
            </div>
            
            {index < steps.length - 1 && (
              <div className="absolute ml-2.5 mt-8 w-0.5 h-6 bg-gray-200" />
            )}
          </div>
        ))}
      </div>
      
      {/* Progress Bar */}
      <div className="mt-6 pt-4 border-t">
        <div className="flex justify-between text-xs text-gray-600 mb-2">
          <span>Progress</span>
          <span>{currentStep}/18 Questions</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${Math.min((currentStep / 18) * 100, 100)}%` }}
          />
        </div>
      </div>
    </div>
  )
}
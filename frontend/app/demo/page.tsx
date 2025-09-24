'use client'

import { useState } from 'react'
import OptionDisplay from '@/components/OptionDisplay'
import { mockQuestionWithMetadata } from '@/utils/mockData'
import { ChevronRight, Info } from 'lucide-react'

export default function DemoPage() {
  const [selectedOption, setSelectedOption] = useState<string>('')

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
            TruScholar Compass Demo
          </h1>
          <p className="text-gray-600">
            Experience how each option reveals your personality, interests, and motivators
          </p>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex items-center gap-2 mb-4">
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
              Question #{mockQuestionWithMetadata.question_number}
            </span>
            <span className="text-gray-500 text-sm">Career Exploration</span>
          </div>

          <h2 className="text-2xl font-semibold text-gray-800 mb-6">
            {mockQuestionWithMetadata.question_text}
          </h2>

          {/* Info Box */}
          <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg mb-6">
            <Info className="w-5 h-5 text-blue-600 mt-0.5" />
            <div className="text-sm text-blue-800">
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
          <div className="space-y-6">
            {mockQuestionWithMetadata.options?.map((option) => (
              <OptionDisplay
                key={option.id}
                option={option}
                isSelected={selectedOption === option.id}
                onSelect={() => setSelectedOption(option.id)}
                disabled={false}
              />
            ))}
          </div>

          {/* Submit Button */}
          <div className="mt-8 flex justify-center">
            <button
              disabled={!selectedOption}
              className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
            >
              Submit Response
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Legend */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Understanding the Metadata</h3>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">RIASEC Dimensions</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li><span className="font-medium">R</span> - Realistic: Hands-on, practical</li>
                <li><span className="font-medium">I</span> - Investigative: Analytical, research</li>
                <li><span className="font-medium">A</span> - Artistic: Creative, expressive</li>
                <li><span className="font-medium">S</span> - Social: Helping, collaborative</li>
                <li><span className="font-medium">E</span> - Enterprising: Leadership, business</li>
                <li><span className="font-medium">C</span> - Conventional: Organized, structured</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Career Motivators</h4>
              <p className="text-sm text-gray-600">
                Shows what drives you: autonomy, growth, purpose, stability, creativity, 
                recognition, team collaboration, challenges, and more.
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Interest Areas</h4>
              <p className="text-sm text-gray-600">
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
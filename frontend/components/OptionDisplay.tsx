'use client'

import { OptionTarget } from '@/types/journey'
import { Brain, Target, Heart, Sparkles } from 'lucide-react'

interface Props {
  option: OptionTarget
  isSelected: boolean
  onSelect: () => void
  disabled?: boolean
  optionIndex?: number
}

const RIASEC_COLORS = {
  realistic: '#8B4513',      // Brown
  investigative: '#4169E1',  // Royal Blue
  artistic: '#9370DB',       // Medium Purple
  social: '#32CD32',         // Lime Green
  enterprising: '#FF8C00',   // Dark Orange
  conventional: '#708090'    // Slate Gray
}

const RIASEC_LABELS = {
  realistic: 'R',
  investigative: 'I',
  artistic: 'A',
  social: 'S',
  enterprising: 'E',
  conventional: 'C'
}

export default function OptionDisplay({ option, isSelected, onSelect, disabled }: Props) {
  // Get top RIASEC dimensions
  const topRiasec = Object.entries(option.riasec_weights || {})
    .sort((a, b) => (b[1] || 0) - (a[1] || 0))
    .slice(0, 3)

  // Get top motivators
  const topMotivators = option.motivators?.slice(0, 3) || []
  
  // Get interests
  const interests = option.interests || []

  return (
    <button
      onClick={onSelect}
      disabled={disabled}
      className={`w-full text-left p-6 rounded-xl border-2 transition-all transform hover:scale-[1.01] ${
        isSelected
          ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-lg'
          : 'border-gray-200 hover:border-gray-300 bg-white hover:bg-gray-50'
      } disabled:opacity-50`}
    >
      <div className="space-y-4">
        {/* Option ID and Text */}
        <div>
          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 text-white font-bold mr-3">
            {option.id}
          </span>
          <span className="text-gray-800 leading-relaxed">{option.text}</span>
        </div>

        {/* Metadata Display */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-100">
          
          {/* RIASEC Weights */}
          <div className="space-y-2">
            <div className="flex items-center gap-1 text-xs font-semibold text-gray-600">
              <Brain className="w-3 h-3" />
              <span>RIASEC Profile</span>
            </div>
            <div className="flex gap-1">
              {topRiasec.map(([dimension, weight]) => (
                <div
                  key={dimension}
                  className="relative group"
                  style={{ 
                    flex: weight || 0,
                    minWidth: '30px'
                  }}
                >
                  <div 
                    className="h-8 rounded flex items-center justify-center text-white text-xs font-bold transition-all hover:scale-105"
                    style={{ 
                      backgroundColor: RIASEC_COLORS[dimension as keyof typeof RIASEC_COLORS],
                      opacity: 0.8 + ((weight || 0) * 0.2)
                    }}
                  >
                    {RIASEC_LABELS[dimension as keyof typeof RIASEC_LABELS]}
                  </div>
                  <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                    {dimension}: {((weight || 0) * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Motivators */}
          <div className="space-y-2">
            <div className="flex items-center gap-1 text-xs font-semibold text-gray-600">
              <Target className="w-3 h-3" />
              <span>Key Motivators</span>
            </div>
            <div className="space-y-1">
              {topMotivators.map((motivator, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-orange-400 to-orange-500 transition-all"
                      style={{ width: `${motivator.weight * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-600 capitalize min-w-[60px]">
                    {motivator.type}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Interests */}
          <div className="space-y-2">
            <div className="flex items-center gap-1 text-xs font-semibold text-gray-600">
              <Heart className="w-3 h-3" />
              <span>Interests</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {interests.map((interest, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gradient-to-r from-pink-100 to-purple-100 text-purple-700"
                >
                  {interest.area}
                  <span className="ml-1 text-purple-500">
                    {(interest.weight * 100).toFixed(0)}%
                  </span>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Confidence Impact */}
        <div className="flex items-center justify-end gap-2 pt-2">
          <Sparkles className="w-4 h-4 text-yellow-500" />
          <span className="text-xs text-gray-500">
            Confidence Impact: +{option.confidence_impact.toFixed(1)}
          </span>
        </div>
      </div>
    </button>
  )
}
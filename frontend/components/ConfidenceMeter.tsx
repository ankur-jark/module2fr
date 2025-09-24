'use client'

import { AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { ConfidenceScore } from '@/types/journey'

interface Props {
  confidence?: ConfidenceScore | null
}

export default function ConfidenceMeter({ confidence }: Props) {
  const getConfidenceColor = (value: number) => {
    if (value >= 85) return 'text-green-600 bg-green-100'
    if (value >= 75) return 'text-blue-600 bg-blue-100'
    if (value >= 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getProgressColor = (value: number) => {
    if (value >= 85) return 'bg-green-600'
    if (value >= 75) return 'bg-blue-600'
    if (value >= 60) return 'bg-yellow-600'
    return 'bg-red-600'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Confidence Metrics</h2>
      
      {/* Overall Confidence */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Confidence</span>
          <span className={`text-2xl font-bold ${confidence ? getConfidenceColor(confidence.overall_confidence).split(' ')[0] : 'text-gray-400'}`}>
            {confidence ? `${confidence.overall_confidence.toFixed(0)}%` : '0%'}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all duration-500 ${confidence ? getProgressColor(confidence.overall_confidence) : 'bg-gray-400'}`}
            style={{ width: `${confidence?.overall_confidence || 0}%` }}
          />
        </div>
      </div>

      {/* Sub-metrics */}
      <div className="space-y-3">
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-600">RIASEC</span>
            <span className="text-xs font-medium">
              {confidence ? `${Object.values(confidence.riasec_confidence).reduce((a, b) => a + b, 0) / 6}`.slice(0, 4) : '0'}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div 
              className="bg-purple-600 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${confidence ? Object.values(confidence.riasec_confidence).reduce((a, b) => a + b, 0) / 6 : 0}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-600">Motivators</span>
            <span className="text-xs font-medium">
              {confidence ? `${confidence.motivator_confidence.toFixed(0)}%` : '0%'}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div 
              className="bg-orange-600 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${confidence?.motivator_confidence || 0}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-600">Interests</span>
            <span className="text-xs font-medium">
              {confidence ? `${confidence.interest_confidence.toFixed(0)}%` : '0%'}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div 
              className="bg-teal-600 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${confidence?.interest_confidence || 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Ready to Complete */}
      {confidence && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center gap-2">
            {confidence.ready_to_complete ? (
              <>
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-sm text-green-600 font-medium">Ready to complete</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-4 h-4 text-yellow-600" />
                <span className="text-sm text-yellow-600 font-medium">Need more data</span>
              </>
            )}
          </div>
          
          {confidence.gaps_remaining.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-600 mb-1">Gaps remaining:</p>
              <ul className="text-xs text-gray-500 space-y-0.5">
                {confidence.gaps_remaining.slice(0, 3).map((gap, i) => (
                  <li key={i}>• {gap}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
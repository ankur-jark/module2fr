'use client'

import { ArrowRight, CheckCircle, AlertCircle, XCircle, RefreshCw } from 'lucide-react'
import { Decision, ConfidenceScore } from '@/types/journey'

interface Props {
  decision?: Decision | null
  confidence?: ConfidenceScore | null
}

export default function DecisionDisplay({ decision, confidence }: Props) {
  const getDecisionIcon = (type?: string) => {
    switch (type) {
      case 'continue': return ArrowRight
      case 'clarify': return AlertCircle
      case 'complete': return CheckCircle
      case 'save_partial': return XCircle
      default: return RefreshCw
    }
  }

  const getDecisionColor = (type?: string) => {
    switch (type) {
      case 'continue': return 'text-blue-600 bg-blue-100'
      case 'clarify': return 'text-yellow-600 bg-yellow-100'
      case 'complete': return 'text-green-600 bg-green-100'
      case 'save_partial': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const Icon = getDecisionIcon(decision?.decision)
  const colors = getDecisionColor(decision?.decision)

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Decision Engine</h2>
      
      {decision ? (
        <div className="space-y-4">
          {/* Current Decision */}
          <div className={`p-4 rounded-lg ${colors.split(' ')[1]}`}>
            <div className="flex items-center gap-3">
              <Icon className={`w-6 h-6 ${colors.split(' ')[0]}`} />
              <div>
                <p className={`font-semibold ${colors.split(' ')[0]}`}>
                  {decision.decision.toUpperCase()}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  {decision.reasoning}
                </p>
              </div>
            </div>
          </div>

          {/* Next Focus */}
          {decision.next_focus && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-xs font-medium text-gray-600 mb-1">Next Focus:</p>
              <p className="text-sm text-gray-900">{decision.next_focus}</p>
            </div>
          )}

          {/* Decision Rules */}
          <div className="pt-4 border-t">
            <p className="text-xs font-medium text-gray-600 mb-2">Decision Rules:</p>
            <div className="space-y-1 text-xs text-gray-500">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${confidence && confidence.overall_confidence >= 85 ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span>≥85% confidence after 12+ questions → Complete</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${confidence && confidence.overall_confidence >= 75 ? 'bg-blue-500' : 'bg-gray-300'}`} />
                <span>≥75% confidence after 15 questions → Complete</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${confidence && confidence.overall_confidence < 75 ? 'bg-yellow-500' : 'bg-gray-300'}`} />
                <span>&lt;75% confidence after 15 questions → Clarify</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <RefreshCw className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p className="text-sm">No decision yet</p>
          <p className="text-xs mt-1">Start a journey to see decision engine in action</p>
        </div>
      )}
    </div>
  )
}
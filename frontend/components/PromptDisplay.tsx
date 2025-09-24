'use client'

import { useState, useEffect } from 'react'
import { Code, Eye, EyeOff } from 'lucide-react'
import { JourneyState } from '@/types/journey'

interface Props {
  currentPrompt: string
  journeyState: JourneyState | null
}

export default function PromptDisplay({ currentPrompt, journeyState }: Props) {
  const [showPrompt, setShowPrompt] = useState(true)
  const [prompts, setPrompts] = useState<any[]>([])

  useEffect(() => {
    if (journeyState?.current_question) {
      // Simulate what the prompt would look like
      const questionPrompt = {
        type: 'question_generation',
        content: `Generate engaging scenario for ${journeyState.demographics?.age || 25}-year-old.
Target: ${journeyState.current_question.target_dimensions?.primary || 'general'}
Secondary: ${journeyState.current_question.target_dimensions?.secondary?.join(', ') || 'none'}
Question #${journeyState.current_question_number}/15`,
        timestamp: new Date()
      }
      setPrompts(prev => [...prev, questionPrompt])
    }
  }, [journeyState?.current_question])

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">GPT-4 Prompts</h2>
        <button
          onClick={() => setShowPrompt(!showPrompt)}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
        >
          {showPrompt ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          {showPrompt ? 'Hide' : 'Show'}
        </button>
      </div>

      {showPrompt && (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {prompts.map((prompt, index) => (
            <div key={index} className="border rounded-lg p-4 bg-gray-50">
              <div className="flex items-center gap-2 mb-2">
                <Code className="w-4 h-4 text-blue-600" />
                <span className="text-xs font-medium text-blue-600">
                  {prompt.type}
                </span>
                <span className="text-xs text-gray-500 ml-auto">
                  {new Date(prompt.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                {prompt.content}
              </pre>
            </div>
          ))}
          
          {prompts.length === 0 && (
            <p className="text-sm text-gray-500 text-center py-8">
              No prompts generated yet. Start a journey to see GPT-4 prompts.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
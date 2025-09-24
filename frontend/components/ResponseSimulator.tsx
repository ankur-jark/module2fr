'use client'

import { useState } from 'react'
import { Send, SkipForward, Sparkles } from 'lucide-react'
import axios from 'axios'

interface Props {
  journeyId: string
  questionId: string
  onResponse: (response: string) => void
}

const sampleResponses = [
  "I enjoy solving complex technical problems and building software solutions that make a real impact.",
  "I prefer working in teams where I can help others grow and collaborate on meaningful projects.",
  "I'm drawn to creative work where I can express myself and think outside the box.",
  "I like organizing data and creating systems that improve efficiency.",
  "Leadership roles energize me - I enjoy making strategic decisions and guiding teams.",
  "Research and analysis fascinate me. I love diving deep into problems to understand root causes.",
]

export default function ResponseSimulator({ journeyId, questionId, onResponse }: Props) {
  const [response, setResponse] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const submitResponse = async (text: string, skipped = false) => {
    setIsSubmitting(true)
    try {
      const result = await axios.post(
        `http://localhost:8000/api/v1/compass/journey/${journeyId}/respond`,
        {
          question_id: questionId,
          response_text: text,
          response_time_seconds: Math.floor(Math.random() * 60) + 20,
          skipped
        }
      )
      
      onResponse(text)
      setResponse('')
      
      // Reload journey state
      window.location.reload()
    } catch (error) {
      console.error('Failed to submit response:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const autofillResponse = () => {
    const randomResponse = sampleResponses[Math.floor(Math.random() * sampleResponses.length)]
    setResponse(randomResponse)
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <textarea
          value={response}
          onChange={(e) => setResponse(e.target.value)}
          placeholder="Type your response here..."
          className="w-full p-3 border border-gray-300 rounded-lg resize-none h-24 pr-12"
          disabled={isSubmitting}
        />
        <button
          onClick={autofillResponse}
          className="absolute right-2 top-2 p-2 text-purple-600 hover:bg-purple-50 rounded-lg"
          title="Auto-fill with sample response"
        >
          <Sparkles className="w-4 h-4" />
        </button>
      </div>
      
      <div className="flex gap-2">
        <button
          onClick={() => submitResponse(response)}
          disabled={!response || isSubmitting}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          Submit Response
        </button>
        
        <button
          onClick={() => submitResponse('', true)}
          disabled={isSubmitting}
          className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
        >
          <SkipForward className="w-4 h-4" />
          Skip Question
        </button>
      </div>
      
      <div className="text-xs text-gray-500">
        <p>• Click sparkle for sample responses</p>
        <p>• Skipping reduces confidence by 10%</p>
      </div>
    </div>
  )
}
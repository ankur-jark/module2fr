'use client'

import { Tag } from 'lucide-react'
import { Interest } from '@/types/journey'

interface Props {
  interests: Interest[]
}

export default function InterestsDisplay({ interests }: Props) {
  const categorizedInterests = interests.reduce((acc, interest) => {
    if (!acc[interest.category]) {
      acc[interest.category] = []
    }
    acc[interest.category].push(interest)
    return acc
  }, {} as Record<string, Interest[]>)

  const getEnthusiasmColor = (enthusiasm: number) => {
    if (enthusiasm >= 8) return 'bg-green-100 text-green-800 border-green-300'
    if (enthusiasm >= 6) return 'bg-blue-100 text-blue-800 border-blue-300'
    if (enthusiasm >= 4) return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    return 'bg-gray-100 text-gray-800 border-gray-300'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Personal Interests</h2>
      
      <div className="space-y-3">
        {Object.entries(categorizedInterests).map(([category, items]) => (
          <div key={category}>
            <h3 className="text-xs font-medium text-gray-600 uppercase mb-2">
              {category}
            </h3>
            <div className="flex flex-wrap gap-2">
              {items.map((interest, index) => (
                <div
                  key={index}
                  className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs border ${getEnthusiasmColor(interest.enthusiasm)}`}
                >
                  <Tag className="w-3 h-3" />
                  <span>{interest.specific}</span>
                  <span className="font-semibold">
                    {interest.enthusiasm.toFixed(0)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
        
        {interests.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-4">
            No interests identified yet
          </p>
        )}
      </div>
      
      {interests.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-gray-600">
            Total interests identified: <span className="font-semibold">{interests.length}</span>
          </p>
        </div>
      )}
    </div>
  )
}
'use client'

import { Clock, Info, AlertCircle, CheckCircle } from 'lucide-react'
import { Event } from '@/types/journey'

interface Props {
  events: Event[]
}

export default function EventLog({ events }: Props) {
  const getEventIcon = (type: string) => {
    if (type.includes('error')) return AlertCircle
    if (type.includes('complete')) return CheckCircle
    return Info
  }

  const getEventColor = (type: string) => {
    if (type.includes('error')) return 'text-red-600'
    if (type.includes('complete')) return 'text-green-600'
    if (type.includes('question')) return 'text-blue-600'
    return 'text-gray-600'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Event Log</h2>
      
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {events.slice().reverse().map((event, index) => {
          const Icon = getEventIcon(event.type)
          const color = getEventColor(event.type)
          
          return (
            <div key={index} className="flex gap-3 p-2 hover:bg-gray-50 rounded">
              <Icon className={`w-4 h-4 mt-0.5 ${color}`} />
              <div className="flex-grow">
                <p className="text-sm text-gray-900">{event.message}</p>
                <p className="text-xs text-gray-500 mt-0.5">
                  {event.timestamp?.toLocaleTimeString()}
                </p>
              </div>
            </div>
          )
        })}
        
        {events.length === 0 && (
          <p className="text-sm text-gray-500 text-center py-8">
            No events yet. Start a journey to see events.
          </p>
        )}
      </div>
    </div>
  )
}
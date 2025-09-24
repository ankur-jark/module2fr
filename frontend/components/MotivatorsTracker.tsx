'use client'

import { TrendingUp, DollarSign, Heart, Target, Users, Award, Lightbulb, Shield, BookOpen, Zap, Trophy, Crown } from 'lucide-react'
import { Motivator } from '@/types/journey'

interface Props {
  motivators: Motivator[]
}

const motivatorIcons: Record<string, any> = {
  'Money & Compensation': DollarSign,
  'Growth & Advancement': TrendingUp,
  'Purpose & Impact': Heart,
  'Autonomy & Independence': Target,
  'Work-Life Balance': Users,
  'Recognition & Status': Award,
  'Creativity & Innovation': Lightbulb,
  'Stability & Security': Shield,
  'Learning & Development': BookOpen,
  'Team & Collaboration': Users,
  'Challenge & Competition': Zap,
  'Leadership & Influence': Crown,
}

export default function MotivatorsTracker({ motivators }: Props) {
  const allMotivators = [
    'Money & Compensation',
    'Growth & Advancement',
    'Purpose & Impact',
    'Autonomy & Independence',
    'Work-Life Balance',
    'Recognition & Status',
    'Creativity & Innovation',
    'Stability & Security',
    'Learning & Development',
    'Team & Collaboration',
    'Challenge & Competition',
    'Leadership & Influence',
  ]

  const motivatorMap = motivators.reduce((acc, m) => {
    acc[m.type] = m
    return acc
  }, {} as Record<string, Motivator>)

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Career Motivators</h2>
      
      <div className="grid grid-cols-2 gap-2">
        {allMotivators.map(type => {
          const motivator = motivatorMap[type]
          const Icon = motivatorIcons[type] || Heart
          const isIdentified = !!motivator
          
          return (
            <div
              key={type}
              className={`p-2 rounded-lg border transition-all ${
                isIdentified 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 bg-gray-50 opacity-50'
              }`}
            >
              <div className="flex items-center gap-2">
                <Icon className={`w-4 h-4 ${isIdentified ? 'text-blue-600' : 'text-gray-400'}`} />
                <div className="flex-grow">
                  <p className={`text-xs font-medium ${isIdentified ? 'text-gray-900' : 'text-gray-500'}`}>
                    {type.split(' & ')[0]}
                  </p>
                  {motivator && (
                    <div className="flex items-center gap-1 mt-1">
                      <div className="flex-grow bg-gray-200 rounded-full h-1">
                        <div 
                          className="bg-blue-600 h-1 rounded-full"
                          style={{ width: `${motivator.strength * 10}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600">
                        {motivator.strength.toFixed(0)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
      
      <div className="mt-4 pt-4 border-t">
        <p className="text-xs text-gray-600">
          Identified: <span className="font-semibold">{motivators.length}/12</span>
        </p>
      </div>
    </div>
  )
}
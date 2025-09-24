'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

interface Props {
  scores?: {
    realistic: number
    investigative: number
    artistic: number
    social: number
    enterprising: number
    conventional: number
  }
}

export default function RIASECTracker({ scores }: Props) {
  const data = [
    { name: 'R', fullName: 'Realistic', value: scores?.realistic || 0 },
    { name: 'I', fullName: 'Investigative', value: scores?.investigative || 0 },
    { name: 'A', fullName: 'Artistic', value: scores?.artistic || 0 },
    { name: 'S', fullName: 'Social', value: scores?.social || 0 },
    { name: 'E', fullName: 'Enterprising', value: scores?.enterprising || 0 },
    { name: 'C', fullName: 'Conventional', value: scores?.conventional || 0 },
  ]

  const radarData = data.map(item => ({
    dimension: item.name,
    score: item.value
  }))

  // Get top 3 codes
  const topCodes = [...data]
    .sort((a, b) => b.value - a.value)
    .slice(0, 3)
    .map(d => d.name)
    .join('')

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">RIASEC Profile</h2>
        {topCodes && (
          <span className="text-2xl font-bold text-blue-600">{topCodes}</span>
        )}
      </div>

      {/* Bar Chart */}
      <div className="h-48 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} />
            <Tooltip 
              content={({ active, payload }) => {
                if (active && payload && payload[0]) {
                  const data = payload[0].payload
                  return (
                    <div className="bg-white p-2 border rounded shadow">
                      <p className="text-sm font-medium">{data.fullName}</p>
                      <p className="text-sm text-blue-600">{data.value.toFixed(1)}%</p>
                    </div>
                  )
                }
                return null
              }}
            />
            <Bar dataKey="value" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Details */}
      <div className="space-y-2 text-xs">
        {data.map((item) => (
          <div key={item.name} className="flex items-center justify-between">
            <span className="text-gray-600">{item.fullName}</span>
            <div className="flex items-center gap-2">
              <div className="w-24 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${item.value}%` }}
                />
              </div>
              <span className="text-gray-900 font-medium w-12 text-right">
                {item.value.toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
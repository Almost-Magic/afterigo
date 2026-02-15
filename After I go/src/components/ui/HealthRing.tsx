import React from 'react'

interface HealthRingProps {
  value: number // 0-100
  label: string
  size?: number
  strokeWidth?: number
  color?: string
  bgColor?: string
}

export const HealthRing: React.FC<HealthRingProps> = ({
  value,
  label,
  size = 120,
  strokeWidth = 8,
  color = '#7C9885', // sage
  bgColor = '#E7E5E4' // warmGray-200
}) => {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (value / 100) * circumference

  // Determine colour based on value
  const getColor = () => {
    if (value >= 80) return color // sage - good
    if (value >= 50) return '#D97706' // amber - fair
    return '#DC2626' // red - needs attention
  }

  const ringColor = color !== '#7C9885' ? color : getColor()

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="health-ring w-full h-full" viewBox={`0 0 ${size} ${size}`}>
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={bgColor}
            strokeWidth={strokeWidth}
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={ringColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="health-ring-circle"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-semibold text-warmGray-800 dark:text-warmGray-100">
            {Math.round(value)}%
          </span>
        </div>
      </div>
      <span className="mt-2 text-sm text-warmGray-600 dark:text-warmGray-400 text-center">
        {label}
      </span>
    </div>
  )
}

// Dashboard health rings component
interface DashboardHealthProps {
  accountsCoverage: number
  messagesWritten: number
  trustedPeople: number
  freshness: number
}

export const DashboardHealth: React.FC<DashboardHealthProps> = ({
  accountsCoverage,
  messagesWritten,
  trustedPeople,
  freshness
}) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <HealthRing
        value={accountsCoverage}
        label="Accounts"
      />
      <HealthRing
        value={messagesWritten}
        label="Messages"
      />
      <HealthRing
        value={trustedPeople}
        label="Trusted People"
      />
      <HealthRing
        value={freshness}
        label="Up to Date"
      />
    </div>
  )
}

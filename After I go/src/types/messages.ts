// Message types
export type MessageType = 'letter' | 'voice' | 'photo_story' | 'video'

// Delivery timing types
export type DeliveryTimingType = 'immediate' | 'delayed' | 'milestone' | 'recurring' | 'date_specific'

// Emotional tone types
export type EmotionalTone = 'peaceful' | 'loving' | 'distressed' | 'angry' | 'anxious' | 'neutral'

// Delivery timing configuration
export interface DeliveryTiming {
  type: DeliveryTimingType
  delayDays?: number // for delayed
  milestoneName?: string // for milestone
  recurringSchedule?: string // for recurring
  specificDate?: Date // for date_specific
}

// Media attachment
export interface MediaAttachment {
  id: string
  type: 'image' | 'audio' | 'video'
  data: string // base64 encoded
  filename: string
  mimeType: string
  size: number
  createdAt: Date
}

// Emotional analysis from AI
export interface EmotionalAnalysis {
  overallTone: EmotionalTone
  confidence: number // 0-100
  flaggedSentences?: { text: string; concern: string }[]
  analysedAt: Date
}

// Main message interface
export interface Message {
  id: string
  recipientId: string
  title: string
  content: string // rich text / markdown
  type: MessageType
  mediaAttachments?: MediaAttachment[]
  deliveryTiming: DeliveryTiming
  emotionalTone?: EmotionalAnalysis
  lastReviewedAt?: Date
  freshnessWarning?: boolean
  createdAt: Date
  updatedAt: Date
}

// Recurring schedule options
export const RECURRING_SCHEDULES = [
  { value: 'annually_christmas', label: 'Every Christmas' },
  { value: 'annually_birthday', label: 'Every birthday' },
  { value: 'anniversary', label: 'Every anniversary' },
  { value: 'new_year', label: 'Every New Year' },
  { value: 'mothers_day', label: 'Every Mother\'s Day' },
  { value: 'fathers_day', label: 'Every Father\'s Day' },
  { value: 'other', label: 'Other recurring date' }
]

// Delayed timing options
export const DELAYED_OPTIONS = [
  { value: 7, label: '1 week after' },
  { value: 14, label: '2 weeks after' },
  { value: 30, label: '1 month after' },
  { value: 90, label: '3 months after' },
  { value: 180, label: '6 months after' },
  { value: 365, label: '1 year after' }
]

// Timeline grouping for visual display
export interface TimelineGroup {
  id: string
  name: string
  order: number
  messages: Message[]
}

export const TIMELINE_GROUPS: { id: DeliveryTimingType; name: string; order: number }[] = [
  { id: 'immediate', name: 'Immediate', order: 0 },
  { id: 'delayed', name: 'Coming Weeks', order: 1 },
  { id: 'milestone', name: 'Milestones', order: 2 },
  { id: 'date_specific', name: 'Specific Dates', order: 3 },
  { id: 'recurring', name: 'Recurring', order: 4 }
]

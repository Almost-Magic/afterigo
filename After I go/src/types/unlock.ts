// Unlock request status
export type UnlockRequestStatus =
  | 'pending'
  | 'blocked_by_owner'
  | 'approved'
  | 'completed'
  | 'expired'
  | 'cancelled'

// Waiting period options
export type WaitingPeriod = 14 | 21 | 30

// Allowed requester types
export type AllowedRequesters = 'designated_only' | 'anyone_with_link' | 'shamir_holders'

// Notification channels
export interface NotificationChannels {
  primaryEmail: string
  backupEmail?: string
  sms?: string
  pushEnabled: boolean
}

// Emergency contact
export interface EmergencyContact {
  name: string
  email: string
  phone?: string
  relationship: string
}

// Unlock settings
export interface UnlockSettings {
  waitingPeriodDays: WaitingPeriod
  allowedRequesters: AllowedRequesters
  notificationChannels: NotificationChannels
  emergencyContact?: EmergencyContact
  requireDeathCertificate: boolean
  requireMultipleRequesters: boolean
  minimumRequesters?: number
}

// Main unlock request interface
export interface UnlockRequest {
  id: string
  requestedBy: {
    name: string
    email: string
    phone?: string
    relationship: string
    shareId?: string
  }
  requestedAt: Date
  reason: string
  supportingInfo?: string
  ownerNotified: {
    email: boolean
    sms: boolean
    push: boolean
    emergencyContact: boolean
  }
  waitingPeriodDays: WaitingPeriod
  expiresAt: Date
  status: UnlockRequestStatus
  blockedAt?: Date
  blockedReason?: string
  completedAt?: Date
}

// Waiting period options
export const WAITING_PERIODS: { value: WaitingPeriod; label: string; description: string }[] = [
  { value: 14, label: '14 days', description: 'Two weeks to review and block if needed' },
  { value: 21, label: '21 days', description: 'Three weeks for thorough review' },
  { value: 30, label: '30 days', description: 'One month for careful consideration' }
]

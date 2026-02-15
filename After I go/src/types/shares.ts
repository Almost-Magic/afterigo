// Share status types
export type ShareStatus = 'draft' | 'pending_acceptance' | 'accepted' | 'active' | 'unlocked'

// Unlock condition types
export type UnlockCondition = 'on_death' | 'on_incapacity' | 'on_date' | 'immediate'

// Relationship types
export type RelationshipType =
  | 'spouse'
  | 'partner'
  | 'child'
  | 'parent'
  | 'sibling'
  | 'grandchild'
  | 'friend'
  | 'executor'
  | 'lawyer'
  | 'accountant'
  | 'financial_advisor'
  | 'other'

// Access permission types
export interface AccessPermissions {
  vault: boolean | 'financial_only' | 'crypto_only' | 'specific'
  vaultCategories?: string[]
  messages: boolean
  wishes: boolean
  financialMap: boolean
  incapacityPlan: boolean
  executorGuide: boolean
  familyGuide: boolean
  ethicalWill: boolean
}

// Conditional access (e.g., age-based)
export interface ConditionalAccess {
  condition: string
  minimumAge?: number
}

// Shamir share piece (encrypted)
export interface ShamirShare {
  index: number
  data: string // encrypted share piece
}

// Main share interface
export interface Share {
  id: string
  recipient: {
    name: string
    email: string
    phone?: string
    relationship: RelationshipType
  }
  accessPermissions: AccessPermissions
  unlockCondition: UnlockCondition
  unlockDate?: Date
  conditionalAccess?: ConditionalAccess
  shamirShare?: ShamirShare
  status: ShareStatus
  createdAt: Date
  updatedAt: Date
}

// Relationship options
export const RELATIONSHIPS: { value: RelationshipType; label: string }[] = [
  { value: 'spouse', label: 'Spouse' },
  { value: 'partner', label: 'Partner' },
  { value: 'child', label: 'Child' },
  { value: 'parent', label: 'Parent' },
  { value: 'sibling', label: 'Sibling' },
  { value: 'grandchild', label: 'Grandchild' },
  { value: 'friend', label: 'Friend' },
  { value: 'executor', label: 'Executor' },
  { value: 'lawyer', label: 'Lawyer' },
  { value: 'accountant', label: 'Accountant' },
  { value: 'financial_advisor', label: 'Financial Advisor' },
  { value: 'other', label: 'Other' }
]

// Access level summary for UI
export interface AccessSummary {
  fullAccess: boolean
  partialAccess: boolean
  modules: string[]
}

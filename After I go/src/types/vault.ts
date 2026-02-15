// Account categories for the digital vault
export type AccountCategory =
  | 'critical'
  | 'financial'
  | 'social'
  | 'cloud'
  | 'shopping'
  | 'work'
  | 'entertainment'
  | 'health'
  | 'other'

// Action to take with account after death
export type AccountAction =
  | 'delete'
  | 'download_then_delete'
  | 'transfer'
  | 'memorialize'
  | 'keep_temporarily'
  | 'contact_support'
  | 'custom'

// Account priority level
export type AccountPriority = 'critical' | 'important' | 'optional'

// 2FA method types
export type TwoFactorMethod = 'totp' | 'sms' | 'email' | 'hardware' | 'none'

// Crypto wallet types
export type WalletType = 'hot' | 'cold' | 'exchange' | 'hardware'

// Security question interface
export interface SecurityQuestion {
  question: string
  answer: string
}

// Crypto wallet details
export interface CryptoDetails {
  walletType: WalletType
  seedPhrase?: string
  derivationPath?: string
  hardwareLocation?: string
  approximateValue?: string
  network?: string
  exchangeName?: string
}

// Main vault account interface
export interface VaultAccount {
  id: string
  category: AccountCategory
  serviceName: string
  url?: string
  username: string
  email?: string
  password: string
  pin?: string
  securityQuestions?: SecurityQuestion[]
  twoFactorMethod?: TwoFactorMethod
  twoFactorBackupCodes?: string[]
  cryptoDetails?: CryptoDetails
  action: AccountAction
  customInstructions?: string
  transferTo?: string
  priority: AccountPriority
  lastVerified?: Date
  notes?: string
  sharedWith: string[]
  createdAt: Date
  updatedAt: Date
}

// Vault health metrics
export interface VaultHealth {
  accountsCoverage: number
  messagesWritten: number
  trustedPeopleAssigned: number
  freshness: number
  overallScore: number
  staleAccounts: string[]
  missingCategories: AccountCategory[]
}

// Category info for UI
export interface CategoryInfo {
  id: AccountCategory
  name: string
  description: string
  icon: string
}

export const CATEGORIES: CategoryInfo[] = [
  { id: 'critical', name: 'Critical Access', description: 'Email, phone, main accounts', icon: '🔑' },
  { id: 'financial', name: 'Financial', description: 'Banks, investments, superannuation', icon: '💰' },
  { id: 'social', name: 'Social Media', description: 'Facebook, Instagram, Twitter/X', icon: '👥' },
  { id: 'cloud', name: 'Cloud Storage', description: 'iCloud, Dropbox, Google Drive', icon: '☁️' },
  { id: 'shopping', name: 'Shopping', description: 'Amazon, eBay, online stores', icon: '🛒' },
  { id: 'work', name: 'Work & Professional', description: 'LinkedIn, work accounts', icon: '💼' },
  { id: 'entertainment', name: 'Entertainment', description: 'Netflix, Spotify, gaming', icon: '🎬' },
  { id: 'health', name: 'Health & Government', description: 'MyHealth, Medicare, ATO', icon: '🏥' },
  { id: 'other', name: 'Other', description: 'Miscellaneous accounts', icon: '📦' }
]

export const PRIORITIES: { value: AccountPriority; label: string }[] = [
  { value: 'critical', label: 'Critical' },
  { value: 'important', label: 'Important' },
  { value: 'optional', label: 'Optional' }
]

export const ACTIONS: { value: AccountAction; label: string }[] = [
  { value: 'delete', label: 'Delete the account' },
  { value: 'download_then_delete', label: 'Download all data, then delete' },
  { value: 'transfer', label: 'Transfer to someone' },
  { value: 'memorialize', label: 'Memorialise (if supported)' },
  { value: 'keep_temporarily', label: 'Keep active temporarily' },
  { value: 'contact_support', label: 'Contact customer support' },
  { value: 'custom', label: 'Custom instructions' }
]

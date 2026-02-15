// Two-factor authentication types
export type TwoFactorType = 'totp' | 'sms' | 'email' | 'hardware' | 'none'

// Encrypted data interface
export interface EncryptedData {
  iv: string
  ciphertext: string
  salt: string
}

// Password strength levels
export type PasswordStrength = 'weak' | 'fair' | 'good' | 'strong'

// Password strength details
export interface PasswordStrengthDetails {
  level: PasswordStrength
  score: number // 0-100
  feedback: string[]
  suggestions: string[]
}

// Encryption status
export interface EncryptionStatus {
  algorithm: string
  keyLength: number
  kdf: string
  iterations: number
  encrypted: boolean
  lastVerified: Date
}

// Shamir configuration
export interface ShamirConfig {
  totalShares: number
  threshold: number
  generated: boolean
  distributedShares: number
}

// Security settings
export interface SecuritySettings {
  masterPasswordHash?: string
  salt?: string
  passwordCheck?: EncryptedData
  twoFactorEnabled: boolean
  twoFactorType: TwoFactorType
  shamirEnabled: boolean
  shamirConfig?: ShamirConfig
  autoLockTimeout: number // minutes
  requireAuthOnResume: boolean
}

// Password requirements
export const PASSWORD_REQUIREMENTS = {
  minLength: 12,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSymbols: true
}

// Check password strength
export function checkPasswordStrength(password: string): PasswordStrengthDetails {
  const feedback: string[] = []
  const suggestions: string[] = []
  let score = 0

  // Length check
  if (password.length >= 12) {
    score += 25
  } else if (password.length >= 8) {
    score += 15
    suggestions.push('Use at least 12 characters for better security')
  } else {
    suggestions.push('Use at least 8 characters')
  }

  // Character variety
  if (/[A-Z]/.test(password)) score += 15
  else suggestions.push('Add uppercase letters')

  if (/[a-z]/.test(password)) score += 15
  else suggestions.push('Add lowercase letters')

  if (/[0-9]/.test(password)) score += 15
  else suggestions.push('Add numbers')

  if (/[^A-Za-z0-9]/.test(password)) score += 15
  else suggestions.push('Add special characters')

  // Bonus for length beyond 16
  if (password.length >= 16) {
    score += 15
    feedback.push('Excellent length')
  }

  // Determine level
  let level: PasswordStrength
  if (score >= 85) {
    level = 'strong'
    feedback.push('Strong password')
  } else if (score >= 60) {
    level = 'good'
    feedback.push('Good password')
  } else if (score >= 40) {
    level = 'fair'
    feedback.push('Fair password')
  } else {
    level = 'weak'
    feedback.push('Weak password')
  }

  return { level, score, feedback, suggestions }
}

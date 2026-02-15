import type { EncryptedData } from '../../types/security'

// Password check constant
const PASSWORD_CHECK_STRING = 'AFTER_I_GO_PASSWORD_CHECK'

// Convert ArrayBuffer to base64 string
export function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return btoa(binary)
}

// Convert base64 string to ArrayBuffer
export function base64ToArrayBuffer(base64: string): ArrayBuffer {
  const binary = atob(base64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return bytes.buffer
}

// Generate a random salt
export function generateSalt(): Uint8Array {
  return crypto.getRandomValues(new Uint8Array(16))
}

// Generate a random IV
export function generateIV(): Uint8Array {
  return crypto.getRandomValues(new Uint8Array(12))
}

// Derive a cryptographic key from a password using PBKDF2
export async function deriveKey(
  password: string,
  salt: Uint8Array
): Promise<CryptoKey> {
  const encoder = new TextEncoder()
  const passwordBuffer = encoder.encode(password)

  // Import the password as a key
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    passwordBuffer,
    'PBKDF2',
    false,
    ['deriveKey']
  )

  // Derive the AES-GCM key
  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: 100000,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  )
}

// Encrypt data using AES-256-GCM
export async function encrypt(
  plaintext: string,
  key: CryptoKey,
  iv: Uint8Array
): Promise<EncryptedData> {
  const encoder = new TextEncoder()
  const data = encoder.encode(plaintext)

  const encrypted = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    data
  )

  return {
    iv: arrayBufferToBase64(iv),
    ciphertext: arrayBufferToBase64(encrypted),
    salt: '' // Salt is passed separately
  }
}

// Encrypt with salt (for unified API)
export async function encryptWithSalt(
  plaintext: string,
  key: CryptoKey,
  salt: Uint8Array
): Promise<EncryptedData> {
  const iv = generateIV()
  const encoder = new TextEncoder()
  const data = encoder.encode(plaintext)

  const encrypted = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    data
  )

  return {
    iv: arrayBufferToBase64(iv),
    ciphertext: arrayBufferToBase64(encrypted),
    salt: arrayBufferToBase64(salt)
  }
}

// Decrypt data using AES-256-GCM
export async function decrypt(
  encrypted: EncryptedData,
  key: CryptoKey
): Promise<string> {
  const decoder = new TextDecoder()
  const iv = base64ToArrayBuffer(encrypted.iv)
  const ciphertext = base64ToArrayBuffer(encrypted.ciphertext)

  const decrypted = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    ciphertext
  )

  return decoder.decode(decrypted)
}

// Create a password check to verify password correctness
export async function createPasswordCheck(
  password: string,
  salt: Uint8Array
): Promise<EncryptedData> {
  const key = await deriveKey(password, salt)
  return encryptWithSalt(PASSWORD_CHECK_STRING, key, salt)
}

// Verify password against stored check
export async function verifyPassword(
  password: string,
  salt: Uint8Array,
  encryptedCheck: EncryptedData
): Promise<boolean> {
  try {
    const key = await deriveKey(password, salt)
    const decrypted = await decrypt(encryptedCheck, key)
    return decrypted === PASSWORD_CHECK_STRING
  } catch {
    return false
  }
}

// Encrypt an object (JSON)
export async function encryptObject<T>(
  obj: T,
  key: CryptoKey,
  salt: Uint8Array
): Promise<EncryptedData> {
  const jsonString = JSON.stringify(obj)
  return encryptWithSalt(jsonString, key, salt)
}

// Decrypt an object (JSON)
export async function decryptObject<T>(
  encrypted: EncryptedData,
  key: CryptoKey
): Promise<T> {
  const jsonString = await decrypt(encrypted, key)
  return JSON.parse(jsonString) as T
}

// Generate a secure random password
export function generateRandomPassword(length: number = 24): string {
  const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const lowercase = 'abcdefghijklmnopqrstuvwxyz'
  const numbers = '0123456789'
  const symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?'
  const all = uppercase + lowercase + numbers + symbols

  let password = ''
  password += uppercase[crypto.getRandomValues(new Uint8Array(1))[0] % uppercase.length]
  password += lowercase[crypto.getRandomValues(new Uint8Array(1))[0] % lowercase.length]
  password += numbers[crypto.getRandomValues(new Uint8Array(1))[0] % numbers.length]
  password += symbols[crypto.getRandomValues(new Uint8Array(1))[0] % symbols.length]

  for (let i = 4; i < length; i++) {
    password += all[crypto.getRandomValues(new Uint8Array(1))[0] % all.length]
  }

  // Shuffle the password
  const shuffled = password.split('').sort(() =>
    crypto.getRandomValues(new Uint8Array(1))[0] - 128
  ).join('')

  return shuffled
}

// Hash a string using SHA-256 (for non-security purposes like checksums)
export async function hashString(text: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(text)
  const hash = await crypto.subtle.digest('SHA-256', data)
  return arrayBufferToBase64(hash)
}

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { deriveKey, createPasswordCheck, verifyPassword, generateSalt } from '../lib/crypto/encryption'
import { settingsOps } from '../lib/storage/database'
import type { EncryptedData } from '../types/security'

interface AuthState {
  isAuthenticated: boolean
  masterKey: CryptoKey | null
  salt: Uint8Array | null
  passwordCheck: EncryptedData | null
  isFirstTime: boolean
  loading: boolean
  error: string | null

  // Actions
  createAccount: (password: string) => Promise<void>
  login: (password: string) => Promise<boolean>
  logout: () => void
  clearError: () => void
  checkIsFirstTime: () => Promise<boolean>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      masterKey: null,
      salt: null,
      passwordCheck: null,
      isFirstTime: true,
      loading: false,
      error: null,

      createAccount: async (password: string) => {
        set({ loading: true, error: null })

        try {
          const salt = generateSalt()
          const passwordCheck = await createPasswordCheck(password, salt)

          // Store password check and salt (encrypted data that verifies password)
          await settingsOps.set('passwordCheck', passwordCheck)
          await settingsOps.set('salt', Array.from(salt))

          // Derive and store the master key in memory only
          const masterKey = await deriveKey(password, salt)

          set({
            isAuthenticated: true,
            masterKey,
            salt,
            passwordCheck,
            isFirstTime: false,
            loading: false
          })
        } catch (error) {
          set({ error: String(error), loading: false })
          throw error
        }
      },

      login: async (password: string) => {
        set({ loading: true, error: null })

        try {
          const passwordCheckStr = await settingsOps.get<string>('passwordCheck')
          const saltArr = await settingsOps.get<number[]>('salt')

          if (!passwordCheckStr || !saltArr) {
            set({ error: 'No account found', loading: false })
            return false
          }

          const salt = new Uint8Array(saltArr)
          const passwordCheck: EncryptedData = JSON.parse(passwordCheckStr)

          // Verify password
          const isValid = await verifyPassword(password, salt, passwordCheck)

          if (!isValid) {
            set({ error: 'Incorrect password', loading: false })
            return false
          }

          // Derive master key
          const masterKey = await deriveKey(password, salt)

          set({
            isAuthenticated: true,
            masterKey,
            salt,
            passwordCheck,
            isFirstTime: false,
            loading: false
          })

          return true
        } catch (error) {
          set({ error: String(error), loading: false })
          return false
        }
      },

      logout: () => {
        set({
          isAuthenticated: false,
          masterKey: null,
          error: null
        })
      },

      clearError: () => {
        set({ error: null })
      },

      checkIsFirstTime: async () => {
        const passwordCheck = await settingsOps.get<string>('passwordCheck')
        const isFirstTime = !passwordCheck
        set({ isFirstTime })
        return isFirstTime
      }
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        isFirstTime: state.isFirstTime
      })
    }
  )
)

// Helper to get the master key
export async function getMasterKey(): Promise<CryptoKey | null> {
  const state = useAuthStore.getState()
  return state.masterKey
}

// Helper to check if authenticated
export function isAuthenticated(): boolean {
  return useAuthStore.getState().isAuthenticated
}

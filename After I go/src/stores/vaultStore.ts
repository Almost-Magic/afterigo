import { create } from 'zustand'
import { encryptObject, decryptObject, deriveKey, generateSalt } from '../lib/crypto/encryption'
import { accountOps, settingsOps } from '../lib/storage/database'
import { useAuthStore } from './authStore'
import type { VaultAccount, VaultHealth, AccountCategory } from '../types/vault'
import type { EncryptedData } from '../types/security'

interface VaultState {
  accounts: VaultAccount[]
  loading: boolean
  error: string | null
  searchQuery: string
  filterCategory: AccountCategory | 'all'

  // Actions
  loadAccounts: () => Promise<void>
  addAccount: (account: Omit<VaultAccount, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>
  updateAccount: (id: string, updates: Partial<VaultAccount>) => Promise<void>
  deleteAccount: (id: string) => Promise<void>
  getAccountsByCategory: (category: AccountCategory) => VaultAccount[]
  getAccountById: (id: string) => VaultAccount | undefined
  getVaultHealth: () => Promise<VaultHealth>
  setSearchQuery: (query: string) => void
  setFilterCategory: (category: AccountCategory | 'all') => void
  clearError: () => void
}

export const useVaultStore = create<VaultState>((set, get) => ({
  accounts: [],
  loading: false,
  error: null,
  searchQuery: '',
  filterCategory: 'all',

  loadAccounts: async () => {
    set({ loading: true, error: null })

    try {
      const masterKey = useAuthStore.getState().masterKey
      if (!masterKey) {
        throw new Error('Not authenticated')
      }

      // Check if accounts are encrypted
      const encryptedAccounts = await settingsOps.get<string>('encryptedAccounts')

      if (encryptedAccounts) {
        // Decrypt accounts
        const encryptedData: EncryptedData = JSON.parse(encryptedAccounts)
        const decrypted = await decryptObject<VaultAccount[]>(encryptedData, masterKey)
        set({ accounts: decrypted, loading: false })
      } else {
        // No accounts yet
        set({ accounts: [], loading: false })
      }
    } catch (error) {
      set({ error: String(error), loading: false })
    }
  },

  addAccount: async (accountData) => {
    set({ loading: true, error: null })

    try {
      const masterKey = useAuthStore.getState().masterKey
      if (!masterKey) {
        throw new Error('Not authenticated')
      }

      const now = new Date()
      const account: VaultAccount = {
        ...accountData,
        id: crypto.randomUUID(),
        createdAt: now,
        updatedAt: now
      }

      const accounts = [...get().accounts, account]

      // Encrypt and save
      const encrypted = await encryptObject(accounts, masterKey, new Uint8Array())
      await settingsOps.set('encryptedAccounts', JSON.stringify(encrypted))

      set({ accounts, loading: false })
    } catch (error) {
      set({ error: String(error), loading: false })
      throw error
    }
  },

  updateAccount: async (id, updates) => {
    set({ loading: true, error: null })

    try {
      const masterKey = useAuthStore.getState().masterKey
      if (!masterKey) {
        throw new Error('Not authenticated')
      }

      const accounts = get().accounts.map(acc =>
        acc.id === id ? { ...acc, ...updates, updatedAt: new Date() } : acc
      )

      // Encrypt and save
      const encrypted = await encryptObject(accounts, masterKey, new Uint8Array())
      await settingsOps.set('encryptedAccounts', JSON.stringify(encrypted))

      set({ accounts, loading: false })
    } catch (error) {
      set({ error: String(error), loading: false })
      throw error
    }
  },

  deleteAccount: async (id) => {
    set({ loading: true, error: null })

    try {
      const masterKey = useAuthStore.getState().masterKey
      if (!masterKey) {
        throw new Error('Not authenticated')
      }

      const accounts = get().accounts.filter(acc => acc.id !== id)

      // Encrypt and save
      const encrypted = await encryptObject(accounts, masterKey, new Uint8Array())
      await settingsOps.set('encryptedAccounts', JSON.stringify(encrypted))

      set({ accounts, loading: false })
    } catch (error) {
      set({ error: String(error), loading: false })
      throw error
    }
  },

  getAccountsByCategory: (category) => {
    return get().accounts.filter(acc => acc.category === category)
  },

  getAccountById: (id) => {
    return get().accounts.find(acc => acc.id === id)
  },

  getVaultHealth: async () => {
    const accounts = get().accounts
    const now = new Date()
    const sixMonthsAgo = new Date(now.getTime() - 180 * 24 * 60 * 60 * 1000)

    // Calculate freshness
    const staleAccounts = accounts.filter(
      acc => !acc.lastVerified || new Date(acc.lastVerified) < sixMonthsAgo
    )

    // Calculate category coverage
    const categories: AccountCategory[] = [
      'critical', 'financial', 'social', 'cloud', 'shopping',
      'work', 'entertainment', 'health', 'other'
    ]
    const missingCategories = categories.filter(cat =>
      !accounts.some(acc => acc.category === cat)
    )

    // Estimate completion (rough heuristic)
    const accountsCoverage = Math.min(100, (accounts.length / 50) * 100)

    // Messages coverage (placeholder - would need message store)
    const messagesWritten = 0

    // Trusted people (placeholder - would need share store)
    const trustedPeopleAssigned = 0

    // Freshness score
    const freshness = accounts.length > 0
      ? Math.max(0, 100 - (staleAccounts.length / accounts.length) * 100)
      : 100

    // Overall score
    const overallScore = Math.round(
      (accountsCoverage + messagesWritten + trustedPeopleAssigned + freshness) / 4
    )

    return {
      accountsCoverage,
      messagesWritten,
      trustedPeopleAssigned,
      freshness,
      overallScore,
      staleAccounts: staleAccounts.map(a => a.id),
      missingCategories
    }
  },

  setSearchQuery: (query) => {
    set({ searchQuery: query })
  },

  setFilterCategory: (category) => {
    set({ filterCategory: category })
  },

  clearError: () => {
    set({ error: null })
  }
}))

// Helper to get filtered accounts
export function getFilteredAccounts(): VaultAccount[] {
  const state = useVaultStore.getState()
  let accounts = state.accounts

  // Apply category filter
  if (state.filterCategory !== 'all') {
    accounts = accounts.filter(acc => acc.category === state.filterCategory)
  }

  // Apply search filter
  if (state.searchQuery) {
    const query = state.searchQuery.toLowerCase()
    accounts = accounts.filter(acc =>
      acc.serviceName.toLowerCase().includes(query) ||
      acc.username.toLowerCase().includes(query) ||
      (acc.email?.toLowerCase().includes(query)) ||
      (acc.notes?.toLowerCase().includes(query))
    )
  }

  return accounts
}

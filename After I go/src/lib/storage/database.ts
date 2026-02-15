import Dexie, { type Table } from 'dexie'
import type { VaultAccount } from '../../types/vault'
import type { Message } from '../../types/messages'
import type { Share } from '../../types/shares'
import type { UnlockRequest, UnlockSettings } from '../../types/unlock'

// Database schema version 1
interface AfterIGoDB extends Dexie {
  accounts: Table<VaultAccount, number>
  messages: Table<Message, number>
  shares: Table<Share, number>
  unlockRequests: Table<UnlockRequest, number>
  settings: Table<{ key: string; value: unknown }, string>
}

// Create database instance
export const db = new Dexie('AfterIGoDB') as AfterIGoDB

// Define schema
db.version(1).stores({
  accounts: '++id, category, serviceName, priority, updatedAt',
  messages: '++id, recipientId, type, updatedAt',
  shares: '++id, status, updatedAt',
  unlockRequests: '++id, status, requestedAt',
  settings: 'key'
})

// Account CRUD operations
export const accountOps = {
  async add(account: Omit<VaultAccount, 'id'>): Promise<number> {
    return db.accounts.add({
      ...account,
      id: undefined
    }) as Promise<number>
  },

  async get(id: number): Promise<VaultAccount | undefined> {
    return db.accounts.get(id)
  },

  async getAll(): Promise<VaultAccount[]> {
    return db.accounts.toArray()
  },

  async update(id: number, updates: Partial<VaultAccount>): Promise<number> {
    return db.accounts.update(id, {
      ...updates,
      updatedAt: new Date()
    }) as Promise<number>
  },

  async delete(id: number): Promise<void> {
    return db.accounts.delete(id)
  },

  async getByCategory(category: string): Promise<VaultAccount[]> {
    return db.accounts.where('category').equals(category).toArray()
  },

  async getByPriority(priority: string): Promise<VaultAccount[]> {
    return db.accounts.where('priority').equals(priority).toArray()
  },

  async count(): Promise<number> {
    return db.accounts.count()
  },

  async clear(): Promise<void> {
    return db.accounts.clear()
  }
}

// Message CRUD operations
export const messageOps = {
  async add(message: Omit<Message, 'id'>): Promise<number> {
    return db.messages.add({
      ...message,
      id: undefined
    }) as Promise<number>
  },

  async get(id: number): Promise<Message | undefined> {
    return db.messages.get(id)
  },

  async getAll(): Promise<Message[]> {
    return db.messages.toArray()
  },

  async update(id: number, updates: Partial<Message>): Promise<number> {
    return db.messages.update(id, {
      ...updates,
      updatedAt: new Date()
    }) as Promise<number>
  },

  async delete(id: number): Promise<void> {
    return db.messages.delete(id)
  },

  async getByRecipient(recipientId: string): Promise<Message[]> {
    return db.messages.where('recipientId').equals(recipientId).toArray()
  },

  async count(): Promise<number> {
    return db.messages.count()
  },

  async clear(): Promise<void> {
    return db.messages.clear()
  }
}

// Share CRUD operations
export const shareOps = {
  async add(share: Omit<Share, 'id'>): Promise<number> {
    return db.shares.add({
      ...share,
      id: undefined
    }) as Promise<number>
  },

  async get(id: number): Promise<Share | undefined> {
    return db.shares.get(id)
  },

  async getAll(): Promise<Share[]> {
    return db.shares.toArray()
  },

  async update(id: number, updates: Partial<Share>): Promise<number> {
    return db.shares.update(id, {
      ...updates,
      updatedAt: new Date()
    }) as Promise<number>
  },

  async delete(id: number): Promise<void> {
    return db.shares.delete(id)
  },

  async getByStatus(status: string): Promise<Share[]> {
    return db.shares.where('status').equals(status).toArray()
  },

  async count(): Promise<number> {
    return db.shares.count()
  },

  async clear(): Promise<void> {
    return db.shares.clear()
  }
}

// Unlock request operations
export const unlockRequestOps = {
  async add(request: Omit<UnlockRequest, 'id'>): Promise<number> {
    return db.unlockRequests.add({
      ...request,
      id: undefined
    }) as Promise<number>
  },

  async get(id: number): Promise<UnlockRequest | undefined> {
    return db.unlockRequests.get(id)
  },

  async getAll(): Promise<UnlockRequest[]> {
    return db.unlockRequests.toArray()
  },

  async update(id: number, updates: Partial<UnlockRequest>): Promise<number> {
    return db.unlockRequests.update(id, updates) as Promise<number>
  },

  async delete(id: number): Promise<void> {
    return db.unlockRequests.delete(id)
  },

  async getByStatus(status: string): Promise<UnlockRequest[]> {
    return db.unlockRequests.where('status').equals(status).toArray()
  },

  async count(): Promise<number> {
    return db.unlockRequests.count()
  },

  async clear(): Promise<void> {
    return db.unlockRequests.clear()
  }
}

// Settings operations
export const settingsOps = {
  async get<T>(key: string): Promise<T | undefined> {
    const result = await db.settings.get(key)
    return result?.value as T | undefined
  },

  async set(key: string, value: unknown): Promise<string> {
    return db.settings.put({ key, value }) as Promise<string>
  },

  async delete(key: string): Promise<void> {
    return db.settings.delete(key)
  },

  async getAll(): Promise<Record<string, unknown>> {
    const all = await db.settings.toArray()
    return all.reduce((acc, { key, value }) => {
      acc[key] = value
      return acc
    }, {} as Record<string, unknown>)
  },

  async clear(): Promise<void> {
    return db.settings.clear()
  }
}

// Database health check
export async function checkDatabaseHealth(): Promise<{
  healthy: boolean
  error?: string
}> {
  try {
    await db.open()
    await db.accounts.count()
    return { healthy: true }
  } catch (error) {
    return { healthy: false, error: String(error) }
  }
}

// Close database
export async function closeDatabase(): Promise<void> {
  return db.close()
}

// Export all data (unencrypted - for debugging)
export async function exportAllData(): Promise<{
  accounts: VaultAccount[]
  messages: Message[]
  shares: Share[]
  unlockRequests: UnlockRequest[]
  settings: Record<string, unknown>
}> {
  return {
    accounts: await accountOps.getAll(),
    messages: await messageOps.getAll(),
    shares: await shareOps.getAll(),
    unlockRequests: await unlockRequestOps.getAll(),
    settings: await settingsOps.getAll()
  }
}

// Clear all data
export async function clearAllData(): Promise<void> {
  await accountOps.clear()
  await messageOps.clear()
  await shareOps.clear()
  await unlockRequestOps.clear()
  await settingsOps.clear()
}

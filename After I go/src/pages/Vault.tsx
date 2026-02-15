import React from 'react'
import { Plus, Search, Filter, Lock, Trash2, Edit, Copy } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Modal } from '../components/ui/Modal'
import { useVaultStore, getFilteredAccounts } from '../stores/vaultStore'
import type { VaultAccount, AccountCategory } from '../types/vault'

const CATEGORIES: AccountCategory[] = [
  'critical',
  'financial',
  'social',
  'cloud',
  'shopping',
  'work',
  'entertainment',
  'health',
  'other'
]

const Vault: React.FC = () => {
  const {
    accounts,
    loading,
    searchQuery,
    filterCategory,
    loadAccounts,
    addAccount,
    updateAccount,
    deleteAccount,
    setSearchQuery,
    setFilterCategory
  } = useVaultStore()

  const [showAddModal, setShowAddModal] = React.useState(false)
  const [editingAccount, setEditingAccount] = React.useState<VaultAccount | null>(null)

  React.useEffect(() => {
    loadAccounts()
  }, [loadAccounts])

  const filteredAccounts = getFilteredAccounts()

  const categoryColors: Record<AccountCategory, string> = {
    critical: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    financial: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    social: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    cloud: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    shopping: 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400',
    work: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    entertainment: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    health: 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400',
    other: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex-1 max-w-md">
          <Input
            placeholder="Search accounts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={<Search className="w-5 h-5" />}
          />
        </div>
        <div className="flex gap-2">
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value as AccountCategory | 'all')}
            className="px-4 py-2 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
          >
            <option value="all">All Categories</option>
            {CATEGORIES.map(cat => (
              <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
            ))}
          </select>
          <Button onClick={() => setShowAddModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Account
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="text-center">
          <p className="text-3xl font-bold text-sage">{accounts.length}</p>
          <p className="text-sm text-warmGray-500">Total Accounts</p>
        </Card>
        <Card className="text-center">
          <p className="text-3xl font-bold text-sage">
            {CATEGORIES.filter(cat => accounts.some(a => a.category === cat)).length}
          </p>
          <p className="text-sm text-warmGray-500">Categories Covered</p>
        </Card>
        <Card className="text-center">
          <p className="text-3xl font-bold text-sage">
            {accounts.filter(a => a.category === 'critical').length}
          </p>
          <p className="text-sm text-warmGray-500">Critical Accounts</p>
        </Card>
      </div>

      {/* Accounts List */}
      <div className="space-y-3">
        {filteredAccounts.length === 0 ? (
          <Card className="text-center py-12">
            <Lock className="w-12 h-12 mx-auto text-warmGray-300 mb-4" />
            <h3 className="text-lg font-medium text-warmGray-900 dark:text-warmGray-100 mb-2">
              {searchQuery || filterCategory !== 'all' ? 'No accounts match your search' : 'No accounts yet'}
            </h3>
            <p className="text-warmGray-500 mb-4">
              {searchQuery || filterCategory !== 'all'
                ? 'Try adjusting your search or filter'
                : 'Add your first account to get started'}
            </p>
            {!searchQuery && filterCategory === 'all' && (
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add Account
              </Button>
            )}
          </Card>
        ) : (
          filteredAccounts.map(account => (
            <Card key={account.id} hover>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-white ${categoryColors[account.category]}`}>
                    <Lock className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-medium text-warmGray-900 dark:text-warmGray-100">
                      {account.serviceName}
                    </h3>
                    <p className="text-sm text-warmGray-500">
                      {account.username}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${categoryColors[account.category]}`}>
                    {account.category}
                  </span>
                  <button
                    onClick={() => setEditingAccount(account)}
                    className="p-2 text-warmGray-400 hover:text-warmGray-600 dark:hover:text-warmGray-300 transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => navigator.clipboard.writeText(account.password)}
                    className="p-2 text-warmGray-400 hover:text-warmGray-600 dark:hover:text-warmGray-300 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteAccount(account.id)}
                    className="p-2 text-warmGray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Add Account Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add Account"
      >
        <AddAccountForm
          onSubmit={async (account) => {
            await addAccount(account)
            setShowAddModal(false)
          }}
          onCancel={() => setShowAddModal(false)}
        />
      </Modal>

      {/* Edit Account Modal */}
      <Modal
        isOpen={!!editingAccount}
        onClose={() => setEditingAccount(null)}
        title="Edit Account"
      >
        {editingAccount && (
          <EditAccountForm
            account={editingAccount}
            onSubmit={async (updates) => {
              await updateAccount(editingAccount.id, updates)
              setEditingAccount(null)
            }}
            onCancel={() => setEditingAccount(null)}
          />
        )}
      </Modal>
    </div>
  )
}

const AddAccountForm: React.FC<{
  onSubmit: (account: Omit<VaultAccount, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>
  onCancel: () => void
}> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = React.useState({
    serviceName: '',
    username: '',
    email: '',
    password: '',
    category: 'other' as AccountCategory,
    notes: '',
    website: '',
    recoveryEmail: '',
    recoveryPhone: '',
    lastVerified: undefined as Date | undefined
  })
  const [loading, setLoading] = React.useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await onSubmit(formData)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Service Name"
        value={formData.serviceName}
        onChange={(e) => setFormData({ ...formData, serviceName: e.target.value })}
        placeholder="e.g., Gmail, Netflix"
        required
      />
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Username / Email"
          value={formData.username}
          onChange={(e) => setFormData({ ...formData, username: e.target.value })}
          placeholder="your@email.com"
          required
        />
        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            Category
          </label>
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value as AccountCategory })}
            className="w-full px-3 py-2 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
          >
            {CATEGORIES.map(cat => (
              <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
            ))}
          </select>
        </div>
      </div>
      <Input
        label="Password"
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        placeholder="••••••••"
        showPasswordToggle
        required
      />
      <Input
        label="Website (optional)"
        value={formData.website}
        onChange={(e) => setFormData({ ...formData, website: e.target.value })}
        placeholder="https://..."
      />
      <div className="flex justify-end gap-3 pt-4">
        <Button variant="secondary" type="button" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" loading={loading}>
          Add Account
        </Button>
      </div>
    </form>
  )
}

const EditAccountForm: React.FC<{
  account: VaultAccount
  onSubmit: (updates: Partial<VaultAccount>) => Promise<void>
  onCancel: () => void
}> = ({ account, onSubmit, onCancel }) => {
  const [formData, setFormData] = React.useState({
    serviceName: account.serviceName,
    username: account.username,
    email: account.email,
    password: account.password,
    category: account.category,
    notes: account.notes || '',
    website: account.website || '',
    recoveryEmail: account.recoveryEmail || '',
    recoveryPhone: account.recoveryPhone || ''
  })
  const [loading, setLoading] = React.useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await onSubmit(formData)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Service Name"
        value={formData.serviceName}
        onChange={(e) => setFormData({ ...formData, serviceName: e.target.value })}
        required
      />
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Username / Email"
          value={formData.username}
          onChange={(e) => setFormData({ ...formData, username: e.target.value })}
          required
        />
        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            Category
          </label>
          <select
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value as AccountCategory })}
            className="w-full px-3 py-2 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
          >
            {CATEGORIES.map(cat => (
              <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
            ))}
          </select>
        </div>
      </div>
      <Input
        label="Password"
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        showPasswordToggle
        required
      />
      <div className="flex justify-end gap-3 pt-4">
        <Button variant="secondary" type="button" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" loading={loading}>
          Save Changes
        </Button>
      </div>
    </form>
  )
}

export default Vault

import React, { useState } from 'react'
import { Plus, Trash2, Lock } from 'lucide-react'

interface CriticalAccountsProps {
  formData: {
    accounts: Array<{
      serviceName: string
      username: string
      email: string
      password: string
      category: string
    }>
  }
  setFormData: React.Dispatch<React.SetStateAction<{
    password: string
    confirmPassword: string
    accounts: Array<{
      serviceName: string
      username: string
      email: string
      password: string
      category: string
    }>
    trustedPerson: { name: string; email: string; phone: string; relationship: string }
    message: { title: string; content: string; recipient: string }
  }>>
  onNext: () => void
}

const CATEGORIES = [
  { value: 'critical', label: 'Critical Access' },
  { value: 'financial', label: 'Financial' },
  { value: 'social', label: 'Social Media' },
  { value: 'cloud', label: 'Cloud Storage' }
]

export const CriticalAccounts: React.FC<CriticalAccountsProps> = ({ formData, setFormData }) => {
  const [newAccount, setNewAccount] = useState({
    serviceName: '',
    username: '',
    email: '',
    password: '',
    category: 'critical'
  })

  const addAccount = () => {
    if (newAccount.serviceName && newAccount.username && newAccount.password) {
      setFormData({
        ...formData,
        accounts: [...formData.accounts, { ...newAccount }]
      })
      setNewAccount({
        serviceName: '',
        username: '',
        email: '',
        password: '',
        category: 'critical'
      })
    }
  }

  const removeAccount = (index: number) => {
    setFormData({
      ...formData,
      accounts: formData.accounts.filter((_, i) => i !== index)
    })
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">
        Start with your critical accounts
      </h2>
      <p className="text-warmGray-600 dark:text-warmGray-400 mb-6">
        Add 3-5 critical accounts to get started. You can add more later.
      </p>

      {/* Added accounts list */}
      {formData.accounts.length > 0 && (
        <div className="mb-6 space-y-2">
          <h3 className="text-sm font-medium text-warmGray-700 dark:text-warmGray-300">
            Accounts added ({formData.accounts.length})
          </h3>
          {formData.accounts.map((account, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-warmGray-50 dark:bg-warmGray-700 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <Lock className="w-4 h-4 text-sage" />
                <div>
                  <p className="font-medium text-warmGray-900 dark:text-warmGray-100">
                    {account.serviceName}
                  </p>
                  <p className="text-sm text-warmGray-500">
                    {account.username}
                  </p>
                </div>
              </div>
              <button
                onClick={() => removeAccount(index)}
                className="p-2 text-warmGray-400 hover:text-red-500 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add new account form */}
      <div className="space-y-4 p-4 border border-warmGray-200 dark:border-warmGray-600 rounded-lg">
        <h3 className="font-medium text-warmGray-900 dark:text-warmGray-100">
          Add an account
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-warmGray-600 dark:text-warmGray-400 mb-1">
              Service Name
            </label>
            <input
              type="text"
              value={newAccount.serviceName}
              onChange={(e) => setNewAccount({ ...newAccount, serviceName: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
              placeholder="e.g., Gmail"
            />
          </div>
          <div>
            <label className="block text-sm text-warmGray-600 dark:text-warmGray-400 mb-1">
              Category
            </label>
            <select
              value={newAccount.category}
              onChange={(e) => setNewAccount({ ...newAccount, category: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
            >
              {CATEGORIES.map(cat => (
                <option key={cat.value} value={cat.value}>{cat.label}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-warmGray-600 dark:text-warmGray-400 mb-1">
              Username / Email
            </label>
            <input
              type="text"
              value={newAccount.username}
              onChange={(e) => setNewAccount({ ...newAccount, username: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
              placeholder="your@email.com"
            />
          </div>
          <div>
            <label className="block text-sm text-warmGray-600 dark:text-warmGray-400 mb-1">
              Password
            </label>
            <input
              type="password"
              value={newAccount.password}
              onChange={(e) => setNewAccount({ ...newAccount, password: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
              placeholder="••••••••"
            />
          </div>
        </div>
        <button
          onClick={addAccount}
          disabled={!newAccount.serviceName || !newAccount.username || !newAccount.password}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-sage text-white rounded-lg hover:bg-sage-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Account
        </button>
      </div>
    </div>
  )
}

import React from 'react'
import { User, Mail, Phone, Heart } from 'lucide-react'

interface TrustedPersonProps {
  formData: {
    trustedPerson: {
      name: string
      email: string
      phone: string
      relationship: string
    }
  }
  setFormData: React.Dispatch<React.SetStateAction<{
    password: string
    confirmPassword: string
    accounts: unknown[]
    trustedPerson: { name: string; email: string; phone: string; relationship: string }
    message: { title: string; content: string; recipient: string }
  }>>
  onNext: () => void
}

const RELATIONSHIPS = [
  'Spouse',
  'Partner',
  'Child',
  'Parent',
  'Sibling',
  'Friend',
  'Executor',
  'Lawyer',
  'Other'
]

export const TrustedPerson: React.FC<TrustedPersonProps> = ({ formData, setFormData }) => {
  return (
    <div>
      <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">
        Who should have access when you can't?
      </h2>
      <p className="text-warmGray-600 dark:text-warmGray-400 mb-6">
        Add a trusted person who can access your vault when the time comes.
      </p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            <User className="inline w-4 h-4 mr-1" />
            Name
          </label>
          <input
            type="text"
            value={formData.trustedPerson.name}
            onChange={(e) => setFormData({
              ...formData,
              trustedPerson: { ...formData.trustedPerson, name: e.target.value }
            })}
            className="w-full px-4 py-3 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
            placeholder="Their full name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            <Mail className="inline w-4 h-4 mr-1" />
            Email
          </label>
          <input
            type="email"
            value={formData.trustedPerson.email}
            onChange={(e) => setFormData({
              ...formData,
              trustedPerson: { ...formData.trustedPerson, email: e.target.value }
            })}
            className="w-full px-4 py-3 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
            placeholder="their@email.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            <Phone className="inline w-4 h-4 mr-1" />
            Phone (optional)
          </label>
          <input
            type="tel"
            value={formData.trustedPerson.phone}
            onChange={(e) => setFormData({
              ...formData,
              trustedPerson: { ...formData.trustedPerson, phone: e.target.value }
            })}
            className="w-full px-4 py-3 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
            placeholder="+61 400 000 000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            <Heart className="inline w-4 h-4 mr-1" />
            Relationship
          </label>
          <select
            value={formData.trustedPerson.relationship}
            onChange={(e) => setFormData({
              ...formData,
              trustedPerson: { ...formData.trustedPerson, relationship: e.target.value }
            })}
            className="w-full px-4 py-3 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
          >
            <option value="">Select a relationship</option>
            {RELATIONSHIPS.map(rel => (
              <option key={rel} value={rel}>{rel}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}

import React from 'react'
import { Mail } from 'lucide-react'

interface FirstMessageProps {
  formData: {
    message: {
      title: string
      content: string
      recipient: string
    }
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

export const FirstMessage: React.FC<FirstMessageProps> = ({ formData, setFormData }) => {
  const wordCount = formData.message.content.split(/\s+/).filter(w => w.length > 0).length

  return (
    <div>
      <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">
        Write one message to someone you love
      </h2>
      <p className="text-warmGray-600 dark:text-warmGray-400 mb-6">
        Even just a few sentences. They will receive this when the time comes.
      </p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            To
          </label>
          <select
            value={formData.message.recipient}
            onChange={(e) => setFormData({
              ...formData,
              message: { ...formData.message, recipient: e.target.value }
            })}
            className="w-full px-4 py-3 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
          >
            <option value="">Select a recipient</option>
            {formData.trustedPerson.name && (
              <option value={formData.trustedPerson.name}>
                {formData.trustedPerson.name} ({formData.trustedPerson.relationship})
              </option>
            )}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            Subject
          </label>
          <input
            type="text"
            value={formData.message.title}
            onChange={(e) => setFormData({
              ...formData,
              message: { ...formData.message, title: e.target.value }
            })}
            className="w-full px-4 py-3 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
            placeholder="e.g., Something I wanted to tell you"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            <Mail className="inline w-4 h-4 mr-1" />
            Message
          </label>
          <textarea
            value={formData.message.content}
            onChange={(e) => setFormData({
              ...formData,
              message: { ...formData.message, content: e.target.value }
            })}
            rows={8}
            className="w-full px-4 py-3 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none resize-none"
            placeholder="Write whatever feels right. There's no wrong way to do this..."
          />
          <p className="text-sm text-warmGray-500 mt-1 text-right">
            {wordCount} words
          </p>
        </div>

        <div className="bg-warmGray-50 dark:bg-warmGray-700 rounded-lg p-4">
          <p className="text-sm text-warmGray-600 dark:text-warmGray-300">
            💡 <strong>Tip:</strong> You can add more messages later, including voice recordings and photos.
          </p>
        </div>
      </div>
    </div>
  )
}

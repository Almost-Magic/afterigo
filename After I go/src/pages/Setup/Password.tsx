import React, { useState, useEffect } from 'react'
import { Eye, EyeOff, AlertTriangle } from 'lucide-react'
import { checkPasswordStrength } from '../../types/security'

interface PasswordProps {
  formData: {
    password: string
    confirmPassword: string
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

export const Password: React.FC<PasswordProps> = ({ formData, setFormData, onNext }) => {
  const [showPassword, setShowPassword] = useState(false)
  const [strength, setStrength] = useState(checkPasswordStrength(''))

  useEffect(() => {
    setStrength(checkPasswordStrength(formData.password))
  }, [formData.password])

  const getStrengthColor = () => {
    switch (strength.level) {
      case 'strong': return 'bg-green-500'
      case 'good': return 'bg-sage'
      case 'fair': return 'bg-amber-500'
      default: return 'bg-red-500'
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">
        Create Your Master Password
      </h2>
      <p className="text-warmGray-600 dark:text-warmGray-400 mb-6">
        This password protects everything. We cannot recover it if you forget it.
        That's a feature, not a limitation.
      </p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            Master Password
          </label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full px-4 py-3 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
              placeholder="Enter a strong password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-warmGray-400"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Password strength indicator */}
        {formData.password && (
          <div className="space-y-2">
            <div className="h-2 bg-warmGray-200 dark:bg-warmGray-700 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${getStrengthColor()}`}
                style={{ width: `${strength.score}%` }}
              />
            </div>
            <p className="text-sm text-warmGray-500">
              {strength.feedback.join(' • ')}
            </p>
            {strength.suggestions.length > 0 && (
              <p className="text-sm text-warmGray-400">
                Suggestions: {strength.suggestions.join(', ')}
              </p>
            )}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-warmGray-700 dark:text-warmGray-300 mb-1">
            Confirm Password
          </label>
          <input
            type={showPassword ? 'text' : 'password'}
            value={formData.confirmPassword}
            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
            className="w-full px-4 py-3 rounded-lg border border-warmGray-200 dark:border-warmGray-600 bg-white dark:bg-warmGray-800 text-warmGray-900 dark:text-warmGray-100 focus:ring-2 focus:ring-sage focus:outline-none"
            placeholder="Confirm your password"
          />
        </div>

        {/* Warning */}
        <div className="flex items-start gap-3 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
          <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-amber-700 dark:text-amber-300">
            <p className="font-medium mb-1">We cannot recover this password</p>
            <p>If you forget it, your data cannot be recovered. Write it down somewhere safe.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

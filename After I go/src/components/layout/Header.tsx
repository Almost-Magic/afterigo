import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock, LogOut, RefreshCw } from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import { useVaultStore } from '../../stores/vaultStore'
import type { VaultHealth } from '../../types/vault'

interface HeaderProps {
  title?: string
}

export const Header: React.FC<HeaderProps> = ({ title }) => {
  const navigate = useNavigate()
  const { logout, isAuthenticated } = useAuthStore()
  const { getVaultHealth } = useVaultStore()
  const [health, setHealth] = useState<VaultHealth | null>(null)

  useEffect(() => {
    getVaultHealth().then(setHealth)
  }, [getVaultHealth])

  const handleLock = () => {
    logout()
    navigate('/')
  }

  const score = health?.overallScore ?? 0

  return (
    <header className="h-16 bg-white dark:bg-warmGray-800 border-b border-warmGray-200 dark:border-warmGray-700 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        {title && (
          <h2 className="text-lg font-semibold text-warmGray-900 dark:text-warmGray-100">
            {title}
          </h2>
        )}
      </div>

      <div className="flex items-center gap-4">
        {/* Health indicator */}
        {health && (
          <div className="flex items-center gap-2 text-sm text-warmGray-500">
            <div
              className={`w-2 h-2 rounded-full ${
                score >= 80
                  ? 'bg-sage'
                  : score >= 50
                  ? 'bg-amber-500'
                  : 'bg-red-500'
              }`}
            />
            <span>Vault Health: {score}%</span>
          </div>
        )}

        {/* Lock button */}
        {isAuthenticated && (
          <button
            onClick={handleLock}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-warmGray-600 hover:bg-warmGray-100 dark:hover:bg-warmGray-700 transition-colors"
            title="Lock vault"
          >
            <Lock className="w-5 h-5" />
            <span className="text-sm font-medium">Lock</span>
          </button>
        )}
      </div>
    </header>
  )
}

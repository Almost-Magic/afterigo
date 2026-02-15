import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Lock,
  Mail,
  Heart,
  DollarSign,
  Users,
  Shield,
  BookOpen,
  Globe,
  Download,
  Settings,
  Sun,
  Moon,
  ChevronRight
} from 'lucide-react'

interface NavItem {
  to: string
  label: string
  icon: React.ReactNode
}

const navItems: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
  { to: '/vault', label: 'Vault', icon: <Lock className="w-5 h-5" /> },
  { to: '/messages', label: 'Messages', icon: <Mail className="w-5 h-5" /> },
  { to: '/wishes', label: 'Wishes', icon: <Heart className="w-5 h-5" /> },
  { to: '/financial', label: 'Financial Map', icon: <DollarSign className="w-5 h-5" /> },
  { to: '/shares', label: 'Shares', icon: <Users className="w-5 h-5" /> },
  { to: '/security', label: 'Security', icon: <Shield className="w-5 h-5" /> },
  { to: '/ethical-will', label: 'Ethical Will', icon: <BookOpen className="w-5 h-5" /> },
  { to: '/platforms', label: 'Platform Legacy', icon: <Globe className="w-5 h-5" /> },
  { to: '/export', label: 'Export', icon: <Download className="w-5 h-5" /> },
]

interface SidebarProps {
  darkMode: boolean
  onToggleDarkMode: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({ darkMode, onToggleDarkMode }) => {
  const location = useLocation()

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-white dark:bg-warmGray-800 border-r border-warmGray-200 dark:border-warmGray-700 flex flex-col z-40">
      {/* Logo */}
      <div className="p-6 border-b border-warmGray-200 dark:border-warmGray-700">
        <h1 className="text-xl font-semibold text-warmGray-900 dark:text-warmGray-100">
          After I Go
        </h1>
        <p className="text-sm text-warmGray-500 dark:text-warmGray-400 mt-1">
          Because love doesn't end
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-3">
          {navItems.map((item) => {
            const isActive = location.pathname === item.to ||
              (item.to !== '/dashboard' && location.pathname.startsWith(item.to))

            return (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  className={`
                    flex items-center gap-3 px-3 py-2.5 rounded-lg
                    transition-colors duration-150 ease-in-out
                    ${isActive
                      ? 'bg-sage text-white'
                      : 'text-warmGray-600 dark:text-warmGray-400 hover:bg-warmGray-100 dark:hover:bg-warmGray-700'
                    }
                  `}
                >
                  {item.icon}
                  <span className="font-medium">{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeIndicator"
                      className="ml-auto"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </motion.div>
                  )}
                </NavLink>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Bottom section */}
      <div className="p-4 border-t border-warmGray-200 dark:border-warmGray-700 space-y-2">
        <NavLink
          to="/settings"
          className={({ isActive }) => `
            flex items-center gap-3 px-3 py-2.5 rounded-lg
            transition-colors duration-150 ease-in-out
            ${isActive
              ? 'bg-sage text-white'
              : 'text-warmGray-600 dark:text-warmGray-400 hover:bg-warmGray-100 dark:hover:bg-warmGray-700'
            }
          `}
        >
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </NavLink>

        <button
          onClick={onToggleDarkMode}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-warmGray-600 dark:text-warmGray-400 hover:bg-warmGray-100 dark:hover:bg-warmGray-700 transition-colors"
        >
          {darkMode ? (
            <>
              <Sun className="w-5 h-5" />
              <span className="font-medium">Light Mode</span>
            </>
          ) : (
            <>
              <Moon className="w-5 h-5" />
              <span className="font-medium">Dark Mode</span>
            </>
          )}
        </button>
      </div>
    </aside>
  )
}

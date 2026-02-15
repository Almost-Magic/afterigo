import React, { useState, useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'

// Page titles based on route
const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/vault': 'Digital Vault',
  '/messages': 'Messages',
  '/wishes': 'Final Wishes',
  '/financial': 'Financial Map',
  '/shares': 'Shares & Access',
  '/security': 'Security',
  '/ethical-will': 'Ethical Will',
  '/platforms': 'Platform Legacy',
  '/export': 'Export',
  '/settings': 'Settings',
}

export const AppShell: React.FC = () => {
  const location = useLocation()
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('darkMode')
      if (saved !== null) {
        return JSON.parse(saved)
      }
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return false
  })

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  const getTitle = () => {
    const path = location.pathname
    // Check for exact match first
    if (pageTitles[path]) {
      return pageTitles[path]
    }
    // Check for nested routes
    for (const [route, title] of Object.entries(pageTitles)) {
      if (path.startsWith(route) && route !== '/dashboard') {
        return title
      }
    }
    return pageTitles['/dashboard']
  }

  return (
    <div className="min-h-screen bg-warmGray-50 dark:bg-warmGray-900">
      <Sidebar darkMode={darkMode} onToggleDarkMode={() => setDarkMode(!darkMode)} />
      <main className="ml-64 min-h-screen">
        <Header title={getTitle()} />
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

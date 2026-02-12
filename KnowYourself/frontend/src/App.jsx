import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import BigFive from './pages/BigFive'
import Archetype from './pages/Archetype'
import Consciousness from './pages/Consciousness'
import Journal from './pages/Journal'
import History from './pages/History'
import Profile from './pages/Profile'

const NAV = [
  { to: '/', label: 'Dashboard', icon: '~' },
  { to: '/big-five', label: 'Big Five', icon: '5' },
  { to: '/archetype', label: 'Archetype', icon: 'A' },
  { to: '/consciousness', label: 'Consciousness', icon: 'C' },
  { to: '/journal', label: 'Journal', icon: 'J' },
  { to: '/history', label: 'History', icon: 'H' },
  { to: '/profile', label: 'Profile', icon: 'P' },
]

export default function App() {
  const [darkMode, setDarkMode] = useState(true)
  const [mobileNav, setMobileNav] = useState(false)

  return (
    <BrowserRouter>
      <div className={darkMode ? '' : 'light-mode'}>
        {/* Header */}
        <header className="sticky top-0 z-50 border-b border-border bg-midnight/90 backdrop-blur-md">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gold-dim">
                <span className="text-lg font-bold text-gold">K</span>
              </div>
              <div>
                <h1 className="text-lg font-bold tracking-tight text-text-primary font-[family-name:var(--font-heading)]">
                  KnowYourself
                </h1>
                <p className="text-xs text-text-muted">Personality & Self-Discovery</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="rounded-lg border border-border px-3 py-1.5 text-sm text-text-secondary hover:border-border-hover hover:text-gold transition-colors"
              >
                {darkMode ? 'Light' : 'Dark'}
              </button>
              <button
                onClick={() => setMobileNav(!mobileNav)}
                className="rounded-lg border border-border px-3 py-1.5 text-sm text-text-secondary md:hidden"
              >
                Menu
              </button>
            </div>
          </div>
        </header>

        <div className="mx-auto flex max-w-7xl flex-1 gap-0 md:gap-6 px-4 py-6">
          {/* Sidebar nav */}
          <nav className={`${mobileNav ? 'block' : 'hidden'} md:block w-full md:w-48 shrink-0`}>
            <ul className="flex flex-col gap-1">
              {NAV.map(n => (
                <li key={n.to}>
                  <NavLink
                    to={n.to}
                    end={n.to === '/'}
                    onClick={() => setMobileNav(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                        isActive
                          ? 'bg-gold-dim text-gold font-medium'
                          : 'text-text-secondary hover:text-text-primary hover:bg-midnight-card'
                      }`
                    }
                  >
                    <span className="flex h-6 w-6 items-center justify-center rounded bg-midnight-card text-xs font-mono">
                      {n.icon}
                    </span>
                    {n.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>

          {/* Main content */}
          <main className="flex-1 min-w-0">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/big-five" element={<BigFive />} />
              <Route path="/archetype" element={<Archetype />} />
              <Route path="/consciousness" element={<Consciousness />} />
              <Route path="/journal" element={<Journal />} />
              <Route path="/history" element={<History />} />
              <Route path="/profile" element={<Profile />} />
            </Routes>
          </main>
        </div>

        {/* Footer */}
        <footer className="border-t border-border py-4 text-center text-xs text-text-muted">
          KnowYourself &middot; Almost Magic Tech Lab &middot; Ground Series
        </footer>
      </div>
    </BrowserRouter>
  )
}

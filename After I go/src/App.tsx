import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Setup from './pages/Setup'
import Vault from './pages/Vault'
import Messages from './pages/Messages'
import Wishes from './pages/Wishes'
import FinancialMap from './pages/FinancialMap'
import Shares from './pages/Shares'
import Security from './pages/Security'
import EthicalWill from './pages/EthicalWill'
import PlatformLegacy from './pages/PlatformLegacy'
import Export from './pages/Export'
import Settings from './pages/Settings'
import RecipientMode from './pages/RecipientMode'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/setup" element={<Setup />} />
      <Route path="/vault" element={<Vault />} />
      <Route path="/messages" element={<Messages />} />
      <Route path="/wishes" element={<Wishes />} />
      <Route path="/financial" element={<FinancialMap />} />
      <Route path="/shares" element={<Shares />} />
      <Route path="/security" element={<Security />} />
      <Route path="/ethical-will" element={<EthicalWill />} />
      <Route path="/platform-legacy" element={<PlatformLegacy />} />
      <Route path="/export" element={<Export />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/recipient" element={<RecipientMode />} />
    </Routes>
  )
}

export default App

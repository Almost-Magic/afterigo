import React from 'react'
import { Moon, Bell, Shield, Download, HelpCircle } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">Settings</h2>
        <p className="text-warmGray-600 dark:text-warmGray-400">Customize your After I Go experience</p>
      </div>
      <Card>
        <h3 className="font-medium mb-4 flex items-center gap-2"><Moon className="w-5 h-5"/>Appearance</h3>
        <div className="flex items-center justify-between">
          <div><p className="font-medium">Dark Mode</p><p className="text-sm text-warmGray-500">Use dark theme</p></div>
          <button className="w-12 h-6 rounded-full bg-sage relative"><span className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"/></button>
        </div>
      </Card>
      <Card>
        <h3 className="font-medium mb-4 flex items-center gap-2"><Bell className="w-5 h-5"/>Notifications</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div><p className="font-medium">Vault Reminders</p><p className="text-sm text-warmGray-500">Get reminded to update</p></div>
            <button className="w-12 h-6 rounded-full bg-warmGray-300 relative"><span className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full"/></button>
          </div>
        </div>
      </Card>
      <Card>
        <h3 className="font-medium mb-4 flex items-center gap-2"><Shield className="w-5 h-5"/>Privacy & Security</h3>
        <div className="space-y-4">
          <div><label className="block text-sm mb-1">Auto-lock timeout</label>
            <select className="w-full px-4 py-2 rounded-lg border dark:bg-warmGray-800">
              <option>5 minutes</option><option>15 minutes</option><option>30 minutes</option>
            </select>
          </div>
        </div>
      </Card>
      <Card>
        <div className="space-y-3">
          <Button variant="secondary" className="w-full justify-start"><Download className="w-4 h-4 mr-2"/>Export All Data</Button>
          <Button variant="ghost" className="w-full justify-start"><HelpCircle className="w-4 h-4 mr-2"/>Help Documentation</Button>
        </div>
      </Card>
    </div>
  )
}
export default SettingsPage

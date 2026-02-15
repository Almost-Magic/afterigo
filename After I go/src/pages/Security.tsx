import React from 'react'
import { Shield, Key, Smartphone, AlertTriangle, Check } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

const Security: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">Security Settings</h2>
        <p className="text-warmGray-600 dark:text-warmGray-400">Protect your vault with additional security measures</p>
      </div>
      <Card className="bg-gradient-to-r from-sage to-sage-dark text-white">
        <div className="flex items-center justify-between">
          <div><p className="text-sm opacity-80">Security Score</p><p className="text-4xl font-bold">85%</p></div>
          <Shield className="w-16 h-16 opacity-50"/>
        </div>
      </Card>
      <Card>
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
            <Smartphone className="w-6 h-6 text-amber-600"/>
          </div>
          <div className="flex-1">
            <h3 className="font-medium mb-1">Two-Factor Authentication</h3>
            <p className="text-sm text-warmGray-500 mb-3">Add an extra layer of security</p>
            <Button variant="secondary" size="sm">Enable 2FA</Button>
          </div>
          <span className="px-3 py-1 rounded-full bg-amber-100 text-amber-700 text-sm">Recommended</span>
        </div>
      </Card>
    </div>
  )
}
export default Security

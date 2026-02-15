import React from 'react'
import { Globe, Facebook, Instagram, Twitter } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

const platforms = [
  { id: 'facebook', name: 'Facebook', icon: <Facebook className="w-5 h-5"/> },
  { id: 'instagram', name: 'Instagram', icon: <Instagram className="w-5 h-5"/> },
  { id: 'twitter', name: 'X (Twitter)', icon: <Twitter className="w-5 h-5"/> },
  { id: 'other', name: 'Other Platforms', icon: <Globe className="w-5 h-5"/> }
]

const PlatformLegacy: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">Platform Legacy</h2>
        <p className="text-warmGray-600 dark:text-warmGray-400">Plan what happens to your social media accounts</p>
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        {platforms.map(p => (
          <Card key={p.id}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-warmGray-100 dark:bg-warmGray-700 flex items-center justify-center">{p.icon}</div>
                <h3 className="font-medium">{p.name}</h3>
              </div>
              <Button variant="ghost" size="sm">Add Account</Button>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <button className="p-2 rounded-lg border border-warmGray-200 dark:border-warmGray-600 text-center hover:bg-warmGray-50 text-sm">Memorialize</button>
              <button className="p-2 rounded-lg border border-warmGray-200 dark:border-warmGray-600 text-center hover:bg-warmGray-50 text-sm">Delete</button>
              <button className="p-2 rounded-lg border border-warmGray-200 dark:border-warmGray-600 text-center hover:bg-warmGray-50 text-sm">Transfer</button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
export default PlatformLegacy

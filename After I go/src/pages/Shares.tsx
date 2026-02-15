import React from 'react'
import { Users } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

const Shares: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">Shares & Access</h2>
        <p className="text-warmGray-600 dark:text-warmGray-400">Manage who has access to what</p>
      </div>
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-medium flex items-center gap-2"><Users className="w-5 h-5"/>Trusted People</h3>
          <Button size="sm">Add Person</Button>
        </div>
        <div className="text-center py-8 text-warmGray-400">
          <Users className="w-12 h-12 mx-auto mb-3 opacity-50"/>
          <p>No trusted people added yet</p>
        </div>
      </Card>
    </div>
  )
}
export default Shares

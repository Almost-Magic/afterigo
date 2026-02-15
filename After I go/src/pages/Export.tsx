import React from 'react'
import { Download, Lock, FileText, File } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

const Export: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">Export Your Data</h2>
        <p className="text-warmGray-600 dark:text-warmGray-400">Create a backup of your vault data</p>
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        {[
          { id: 'encrypted', name: 'Encrypted Archive', desc: 'Password-protected ZIP', icon: <Lock className="w-6 h-6"/> },
          { id: 'pdf', name: 'PDF Document', desc: 'Human-readable format', icon: <FileText className="w-6 h-6"/> },
          { id: 'json', name: 'JSON Export', desc: 'Raw data backup', icon: <File className="w-6 h-6"/> }
        ].map(opt => (
          <Card key={opt.id} hover className="cursor-pointer">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 rounded-xl bg-sage/10 flex items-center justify-center text-sage">{opt.icon}</div>
              <div><h3 className="font-medium">{opt.name}</h3><p className="text-sm text-warmGray-500">{opt.desc}</p></div>
            </div>
          </Card>
        ))}
      </div>
      <div className="flex justify-end">
        <Button size="lg"><Download className="w-5 h-5 mr-2"/>Export Data</Button>
      </div>
    </div>
  )
}
export default Export

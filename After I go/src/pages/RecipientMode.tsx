import React, { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Lock, HeartHandshake } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Card } from '../components/ui/Card'

const RecipientMode: React.FC = () => {
  const [searchParams] = useSearchParams()
  const [step, setStep] = useState<'intro' | 'verify' | 'access'>('intro')
  const [password, setPassword] = useState('')

  if (step === 'intro') {
    return (
      <div className="min-h-screen bg-warmGray-50 dark:bg-warmGray-900 flex items-center justify-center p-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-md w-full">
          <Card className="text-center p-8">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-sage/10 flex items-center justify-center">
              <HeartHandshake className="w-10 h-10 text-sage"/>
            </div>
            <h1 className="text-3xl font-light text-warmGray-900 dark:text-warmGray-100 mb-2">Someone left something for you</h1>
            <p className="text-warmGray-600 dark:text-warmGray-400 mb-8">You've been given access to something special. Take your time.</p>
            <div className="space-y-3">
              <Button onClick={() => setStep('verify')} size="lg" className="w-full">I'm ready</Button>
            </div>
          </Card>
        </motion.div>
      </div>
    )
  }

  if (step === 'verify') {
    return (
      <div className="min-h-screen bg-warmGray-50 dark:bg-warmGray-900 flex items-center justify-center p-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-md w-full">
          <Card className="p-8">
            <div className="text-center mb-8">
              <Lock className="w-12 h-12 mx-auto mb-4 text-sage"/>
              <h1 className="text-2xl font-semibold mb-2">Protected Content</h1>
              <p className="text-warmGray-600">Enter the password they shared with you</p>
            </div>
            <div className="space-y-4">
              <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter password"/>
              <Button onClick={() => setStep('access')} className="w-full" size="lg">Unlock</Button>
            </div>
          </Card>
        </motion.div>
      </div>
    )
  }

  return null
}
export default RecipientMode

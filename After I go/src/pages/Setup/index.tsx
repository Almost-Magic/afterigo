import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, ArrowRight, Check } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { useAuthStore } from '../../stores/authStore'
import { Password } from './Password'
import { CriticalAccounts } from './CriticalAccounts'
import { TrustedPerson } from './TrustedPerson'
import { FirstMessage } from './FirstMessage'
import { Complete } from './Complete'

const steps = [
  { component: Password, title: 'Password' },
  { component: CriticalAccounts, title: 'Critical Accounts' },
  { component: TrustedPerson, title: 'Trusted Person' },
  { component: FirstMessage, title: 'First Message' },
  { component: Complete, title: 'Complete' }
]

const Setup: React.FC = () => {
  const navigate = useNavigate()
  const { createAccount, isAuthenticated } = useAuthStore()
  const [currentStep, setCurrentStep] = useState(0)
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
    accounts: [] as Array<{
      serviceName: string
      username: string
      email: string
      password: string
      category: string
    }>,
    trustedPerson: {
      name: '',
      email: '',
      phone: '',
      relationship: ''
    },
    message: {
      title: '',
      content: '',
      recipient: ''
    }
  })

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  const canProceed = () => {
    switch (currentStep) {
      case 0: // Password
        return formData.password.length >= 12 &&
          formData.password === formData.confirmPassword
      case 1: // Critical Accounts
        return formData.accounts.length >= 1
      case 2: // Trusted Person
        return formData.trustedPerson.name && formData.trustedPerson.email
      case 3: // First Message
        return formData.message.title && formData.message.content
      default:
        return true
    }
  }

  const handleNext = async () => {
    if (currentStep === steps.length - 1) {
      try {
        await createAccount(formData.password)
        navigate('/dashboard')
      } catch (error) {
        console.error('Failed to create account:', error)
      }
    } else {
      setCurrentStep(prev => prev + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const CurrentStepComponent = steps[currentStep].component

  return (
    <div className="min-h-screen bg-warmGray-50 dark:bg-warmGray-900 flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            {steps.map((_, index) => (
              <div key={index} className="flex items-center">
                <div
                  className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                    ${index < currentStep
                      ? 'bg-sage text-white'
                      : index === currentStep
                      ? 'bg-sage text-white ring-4 ring-sage/20'
                      : 'bg-warmGray-200 dark:bg-warmGray-700 text-warmGray-500'
                    }
                  `}
                >
                  {index < currentStep ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    index + 1
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`w-full h-1 mx-2 rounded ${
                      index < currentStep
                        ? 'bg-sage'
                        : 'bg-warmGray-200 dark:bg-warmGray-700'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-warmGray-500 mt-4">
            Step {currentStep + 1} of {steps.length}: {steps[currentStep].title}
          </p>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="bg-white dark:bg-warmGray-800 rounded-2xl shadow-xl p-8"
          >
            <CurrentStepComponent
              formData={formData}
              setFormData={setFormData}
              onNext={handleNext}
              onBack={handleBack}
            />
          </motion.div>
        </AnimatePresence>

        <div className="flex justify-between mt-6">
          <Button
            variant="ghost"
            onClick={handleBack}
            disabled={currentStep === 0}
            className={currentStep === 0 ? 'invisible' : ''}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <Button onClick={handleNext} disabled={!canProceed()}>
            {currentStep === steps.length - 1 ? (
              <>Complete Setup</>
            ) : (
              <>
                Next
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default Setup

import React from 'react'
import confetti from 'canvas-confetti'

interface CompleteProps {
  onNext: () => void
}

export const Complete: React.FC<CompleteProps> = ({ onNext }) => {
  const handleComplete = () => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#7C9885', '#A3C4AD', '#5F7161', '#D6D3D1']
    })
    onNext()
  }

  return (
    <div className="text-center">
      <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-sage/10 flex items-center justify-center">
        <span className="text-4xl">🎉</span>
      </div>
      <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">
        You've done something beautiful
      </h2>
      <p className="text-warmGray-600 dark:text-warmGray-400 mb-6">
        You've just done more than 95% of people. Your family is a little safer now.
      </p>

      <div className="bg-warmGray-50 dark:bg-warmGray-700 rounded-lg p-6 mb-6 text-left">
        <h3 className="font-medium text-warmGray-900 dark:text-warmGray-100 mb-3">
          What you've set up:
        </h3>
        <ul className="space-y-2 text-warmGray-600 dark:text-warmGray-300">
          <li className="flex items-center gap-2">
            <span className="text-sage">✓</span> Master password protection
          </li>
          <li className="flex items-center gap-2">
            <span className="text-sage">✓</span> Critical accounts secured
          </li>
          <li className="flex items-center gap-2">
            <span className="text-sage">✓</span> Trusted person designated
          </li>
          <li className="flex items-center gap-2">
            <span className="text-sage">✓</span> First message written
          </li>
        </ul>
      </div>

      <p className="text-warmGray-500 dark:text-warmGray-400 mb-6">
        Come back anytime to add more accounts, write more messages, and complete your legacy.
      </p>

      <button
        onClick={handleComplete}
        className="px-8 py-3 bg-sage text-white rounded-lg hover:bg-sage-dark transition-colors font-medium"
      >
        Go to Dashboard
      </button>
    </div>
  )
}

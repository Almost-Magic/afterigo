import React from 'react'
import { motion } from 'framer-motion'

interface BreathingSpaceProps {
  message?: string
  size?: 'sm' | 'md' | 'lg'
}

const sizeStyles = {
  sm: 'py-8',
  md: 'py-12',
  lg: 'py-16'
}

export const BreathingSpace: React.FC<BreathingSpaceProps> = ({
  message = 'Take a moment if you need to.',
  size = 'md'
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`flex flex-col items-center justify-center text-center ${sizeStyles[size]}`}
    >
      <motion.div
        className="w-16 h-16 rounded-full bg-sage/20 flex items-center justify-center mb-4"
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.6, 1, 0.6]
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      >
        <svg
          className="w-8 h-8 text-sage"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
          />
        </svg>
      </motion.div>
      <p className="text-warmGray-500 dark:text-warmGray-400 italic">
        {message}
      </p>
    </motion.div>
  )
}

// Full-page breathing space for recipient mode
export const FullPageBreathingSpace: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-40 bg-warmGray-50/95 dark:bg-warmGray-900/95 flex items-center justify-center"
    >
      <div className="text-center max-w-md mx-auto px-6">
        <motion.div
          className="w-24 h-24 mx-auto rounded-full bg-sage/20 flex items-center justify-center mb-6"
          animate={{
            scale: [1, 1.15, 1],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        >
          <svg
            className="w-12 h-12 text-sage"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
            />
          </svg>
        </motion.div>
        <h2 className="text-2xl font-light text-warmGray-700 dark:text-warmGray-300 mb-2">
          Take your time
        </h2>
        <p className="text-warmGray-500 dark:text-warmGray-400">
          There's no rush. This is for you, whenever you're ready.
        </p>
      </div>
    </motion.div>
  )
}

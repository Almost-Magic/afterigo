import React from 'react'
import { motion } from 'framer-motion'

interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
  onClick?: () => void
}

const paddingStyles = {
  none: '',
  sm: 'p-3',
  md: 'p-4',
  lg: 'p-6'
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hover = false,
  padding = 'md',
  onClick
}) => {
  const Component = hover ? motion.div : 'div'
  const hoverProps = hover ? {
    whileHover: { y: -2 },
    transition: { duration: 0.2 }
  } : {}

  return (
    <Component
      className={`
        bg-white dark:bg-warmGray-800
        rounded-xl border border-warmGray-200 dark:border-warmGray-700
        ${paddingStyles[padding]}
        ${hover ? 'card-hover cursor-pointer shadow-sm hover:shadow-md' : ''}
        ${className}
      `}
      onClick={onClick}
      {...hoverProps}
    >
      {children}
    </Component>
  )
}

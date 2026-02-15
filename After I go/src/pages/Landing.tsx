import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Lock, Heart, Shield, ArrowRight, Check } from 'lucide-react'
import { Button } from '../components/ui/Button'

const features = [
  {
    icon: <Lock className="w-8 h-8" />,
    title: 'Encrypted Vault',
    description: 'Your passwords and accounts, protected with military-grade encryption that only you hold the keys to.'
  },
  {
    icon: <Heart className="w-8 h-8" />,
    title: 'Messages to Loved Ones',
    description: 'Write letters, record voice messages, and share photos. Delivered when they need them most.'
  },
  {
    icon: <Shield className="w-8 h-8" />,
    title: 'Secure Sharing',
    description: 'Control exactly who sees what. Your family, your rules, your timing.'
  }
]

const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-warmGray-50 dark:bg-warmGray-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-5">
          <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="currentColor" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="100" height="100" fill="url(#grid)" />
          </svg>
        </div>

        <div className="relative max-w-6xl mx-auto px-6 py-24 md:py-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h1 className="text-5xl md:text-7xl font-light text-warmGray-900 dark:text-warmGray-100 mb-6">
              After I Go
            </h1>
            <p className="text-xl md:text-2xl text-warmGray-600 dark:text-warmGray-400 max-w-2xl mx-auto mb-8">
              Because love doesn't end when life does.
            </p>
            <p className="text-lg text-warmGray-500 dark:text-warmGray-400 max-w-xl mx-auto mb-12">
              A private vault that helps the right people find what they need after you're gone.
              Free forever. No cloud. No tracking. Everything stays on your device.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/setup">
                <Button size="lg" className="w-full sm:w-auto">
                  Get Started
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Link to="#learn-more">
                <Button variant="secondary" size="lg" className="w-full sm:w-auto">
                  Learn More
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="learn-more" className="py-24 bg-white dark:bg-warmGray-800">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="text-center p-6"
              >
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-sage/10 flex items-center justify-center text-sage">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">
                  {feature.title}
                </h3>
                <p className="text-warmGray-600 dark:text-warmGray-400">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Privacy Section */}
      <section className="py-24 bg-warmGray-50 dark:bg-warmGray-900">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Shield className="w-16 h-16 mx-auto mb-6 text-sage" />
            <h2 className="text-3xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-4">
              Your data stays on your device. Always.
            </h2>
            <p className="text-lg text-warmGray-600 dark:text-warmGray-400 mb-8">
              After I Go uses AES-256 encryption — the same standard used by banks and military.
              Your master password never leaves your device. We literally cannot see your data,
              even if we wanted to. And we don't want to.
            </p>
            <ul className="text-left inline-block space-y-3 text-warmGray-600 dark:text-warmGray-400">
              {[
                'No cloud storage',
                'No servers',
                'No tracking',
                'No analytics',
                'No data collection',
                'No external API calls'
              ].map((item) => (
                <li key={item} className="flex items-center gap-2">
                  <Check className="w-5 h-5 text-sage" />
                  {item}
                </li>
              ))}
            </ul>
          </motion.div>
        </div>
      </section>

      {/* Open Source Section */}
      <section className="py-24 bg-white dark:bg-warmGray-800">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-4">
              Free forever. Open source. Verify everything.
            </h2>
            <p className="text-lg text-warmGray-600 dark:text-warmGray-400 mb-8">
              After I Go is a gift (dāna). No monetisation. No subscription.
              No "premium tier." It's free because preparing for the inevitable
              shouldn't cost anything.
            </p>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-warmGray-100 dark:bg-warmGray-700 rounded-lg">
              <span className="text-warmGray-600 dark:text-warmGray-300">
                MIT License
              </span>
              <span className="text-warmGray-400">•</span>
              <span className="text-warmGray-600 dark:text-warmGray-300">
                GitHub
              </span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-warmGray-50 dark:bg-warmGray-900 border-t border-warmGray-200 dark:border-warmGray-800">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <p className="text-warmGray-500 dark:text-warmGray-400 mb-4">
            Made with care by{' '}
            <span className="font-semibold">Mani Padisetti</span>
          </p>
          <p className="text-warmGray-400 dark:text-warmGray-500 text-sm">
            Almost Magic Tech Lab • MIT License
          </p>
          <p className="text-warmGray-400 dark:text-warmGray-500 text-sm mt-2">
            After I Go v3.0
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Landing

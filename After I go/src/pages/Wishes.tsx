import React from 'react'
import { Heart, FileText, Music, Video } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

interface Wish {
  id: string
  category: 'final-arrangements' | 'personal-messages' | 'digital-legacy' | 'values'
  title: string
  content: string
  createdAt: Date
}

const Wishes: React.FC = () => {
  const [wishes, setWishes] = React.useState<Wish[]>([])

  const categories = [
    {
      id: 'final-arrangements',
      label: 'Final Arrangements',
      icon: <Heart className="w-5 h-5" />,
      description: 'Your preferences for ceremonies and services'
    },
    {
      id: 'personal-messages',
      label: 'Personal Messages',
      icon: <FileText className="w-5 h-5" />,
      description: 'Letters to specific people'
    },
    {
      id: 'digital-legacy',
      label: 'Digital Legacy',
      icon: <Music className="w-5 h-5" />,
      description: 'Music, photos, and media preferences'
    },
    {
      id: 'values',
      label: 'Values & Wisdom',
      icon: <Video className="w-5 h-5" />,
      description: 'What you want remembered'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">
          Final Wishes
        </h2>
        <p className="text-warmGray-600 dark:text-warmGray-400">
          Document your final wishes and preferences for your loved ones
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {categories.map(cat => {
          const count = wishes.filter(w => w.category === cat.id).length
          return (
            <Card key={cat.id} className="text-center">
              <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-sage/10 flex items-center justify-center text-sage">
                {cat.icon}
              </div>
              <p className="text-2xl font-bold text-warmGray-900 dark:text-warmGray-100">
                {count}
              </p>
              <p className="text-xs text-warmGray-500">{cat.label}</p>
            </Card>
          )
        })}
      </div>

      {/* Category Sections */}
      <div className="space-y-6">
        {categories.map(cat => {
          const categoryWishes = wishes.filter(w => w.category === cat.id)
          return (
            <div key={cat.id}>
              <h3 className="text-lg font-medium text-warmGray-900 dark:text-warmGray-100 mb-3 flex items-center gap-2">
                {cat.icon}
                {cat.label}
              </h3>
              <p className="text-sm text-warmGray-500 mb-3">{cat.description}</p>

              {categoryWishes.length === 0 ? (
                <Card className="border-dashed">
                  <p className="text-center text-warmGray-500 py-4">
                    No wishes recorded yet
                  </p>
                </Card>
              ) : (
                <div className="space-y-3">
                  {categoryWishes.map(wish => (
                    <Card key={wish.id}>
                      <h4 className="font-medium text-warmGray-900 dark:text-warmGray-100 mb-2">
                        {wish.title}
                      </h4>
                      <p className="text-warmGray-600 dark:text-warmGray-400 text-sm">
                        {wish.content}
                      </p>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Add Wish Button */}
      <div className="flex justify-center pt-6">
        <Button size="lg">
          <Heart className="w-5 h-5 mr-2" />
          Add New Wish
        </Button>
      </div>
    </div>
  )
}

export default Wishes

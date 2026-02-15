import React from 'react'
import { BookOpen, Sparkles, Heart, PenTool } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'

const EthicalWill: React.FC = () => {
  const sections = [
    { id: 'life-lessons', title: 'Life Lessons', icon: <Sparkles className="w-5 h-5"/>, prompt: 'What are the most important lessons you\'ve learned?' },
    { id: 'values', title: 'Core Values', icon: <Heart className="w-5 h-5"/>, prompt: 'What values guided your decisions?' },
    { id: 'wisdom', title: 'Wisdom to Share', icon: <BookOpen className="w-5 h-5"/>, prompt: 'What wisdom would you pass on?' }
  ]
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">Ethical Will</h2>
        <p className="text-warmGray-600 dark:text-warmGray-400">Document your values and wisdom to pass on</p>
      </div>
      <div className="grid gap-4">
        {sections.map(section => (
          <Card key={section.id} hover>
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-sage/10 flex items-center justify-center text-sage">{section.icon}</div>
              <div className="flex-1">
                <h3 className="font-medium mb-1">{section.title}</h3>
                <p className="text-sm text-warmGray-500 mb-2">{section.prompt}</p>
                <Button size="sm" variant="secondary"><PenTool className="w-4 h-4 mr-2"/>Write</Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
export default EthicalWill

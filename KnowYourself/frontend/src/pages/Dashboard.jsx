import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getHealth, getProfile, getDailyPrompt } from '../api'
import Card from '../components/Card'
import TraitBar from '../components/TraitBar'

const TRAIT_COLORS = {
  openness: 'bg-purple',
  conscientiousness: 'bg-teal',
  extraversion: 'bg-gold',
  agreeableness: 'bg-green',
  neuroticism: 'bg-rose',
}

const ASSESSMENTS = [
  { to: '/big-five', label: 'Big Five Personality', desc: '50 questions based on IPIP-NEO-PI', color: 'border-gold' },
  { to: '/archetype', label: 'Jungian Archetype', desc: '24 forced-choice questions', color: 'border-teal' },
  { to: '/consciousness', label: 'Consciousness Level', desc: "10 items on Hawkins' scale", color: 'border-purple' },
  { to: '/journal', label: 'Daily Journal', desc: 'AI-guided self-inquiry', color: 'border-rose' },
]

export default function Dashboard() {
  const [health, setHealth] = useState(null)
  const [profile, setProfile] = useState(null)
  const [prompt, setPrompt] = useState(null)

  useEffect(() => {
    getHealth().then(setHealth).catch(() => {})
    getProfile().then(setProfile).catch(() => {})
    getDailyPrompt().then(setPrompt).catch(() => {})
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Welcome to KnowYourself</h1>
        <p className="mt-1 text-text-secondary">
          Personality assessment and self-discovery tools
        </p>
      </div>

      {/* Status */}
      {health && (
        <div className="flex items-center gap-2 text-sm text-green">
          <div className="h-2 w-2 rounded-full bg-green animate-pulse" />
          API v{health.version} online
        </div>
      )}

      {/* Daily prompt */}
      {prompt && (
        <Card className="border-gold/30 bg-gold-dim/30">
          <p className="text-sm text-text-muted mb-1">Today's Reflection Prompt</p>
          <p className="text-lg text-gold italic">"{prompt.prompt}"</p>
          <Link to="/journal" className="mt-3 inline-block text-sm text-gold hover:underline">
            Write in journal &rarr;
          </Link>
        </Card>
      )}

      {/* Assessment cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {ASSESSMENTS.map(a => (
          <Link key={a.to} to={a.to} className="group">
            <Card className={`border-l-4 ${a.color} transition-all group-hover:border-border-hover`}>
              <h3 className="font-semibold text-text-primary group-hover:text-gold transition-colors">
                {a.label}
              </h3>
              <p className="mt-1 text-sm text-text-muted">{a.desc}</p>
            </Card>
          </Link>
        ))}
      </div>

      {/* Latest Big Five scores */}
      {profile?.latest_big_five && (
        <Card title="Latest Big Five Scores">
          {Object.entries(profile.latest_big_five).map(([trait, val]) => (
            <TraitBar
              key={trait}
              label={trait.charAt(0).toUpperCase() + trait.slice(1)}
              value={val}
              color={TRAIT_COLORS[trait] || 'bg-gold'}
            />
          ))}
        </Card>
      )}

      {/* Stats */}
      {profile && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Card>
            <p className="text-2xl font-bold text-gold">{profile.total_assessments}</p>
            <p className="text-xs text-text-muted">Assessments</p>
          </Card>
          <Card>
            <p className="text-2xl font-bold text-teal">{profile.total_journal_entries}</p>
            <p className="text-xs text-text-muted">Journal Entries</p>
          </Card>
          <Card>
            <p className="text-2xl font-bold text-purple">
              {profile.latest_consciousness?.level || '--'}
            </p>
            <p className="text-xs text-text-muted">Consciousness Level</p>
          </Card>
          <Card>
            <p className="text-2xl font-bold text-rose">
              {profile.latest_archetype?.primary_archetype || '--'}
            </p>
            <p className="text-xs text-text-muted">Primary Archetype</p>
          </Card>
        </div>
      )}
    </div>
  )
}

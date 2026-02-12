import { useEffect, useState } from 'react'
import { getProfile } from '../api'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts'
import Card from '../components/Card'
import Loading from '../components/Loading'
import TraitBar from '../components/TraitBar'

const TRAIT_COLORS = {
  openness: 'bg-purple',
  conscientiousness: 'bg-teal',
  extraversion: 'bg-gold',
  agreeableness: 'bg-green',
  neuroticism: 'bg-rose',
}

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getProfile()
      .then(setProfile)
      .catch(e => { setError(e.message); setLoading(false) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loading text="Loading profile..." />
  if (error) return <p className="text-rose">{error}</p>

  const bf = profile.latest_big_five
  const radarData = bf ? Object.entries(bf).map(([k, v]) => ({
    trait: k.charAt(0).toUpperCase() + k.slice(1),
    value: v,
  })) : []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-text-primary">Your Profile</h1>

      {/* Stats row */}
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
          <p className="text-xs text-text-muted">Consciousness</p>
        </Card>
        <Card>
          <p className="text-2xl font-bold text-rose">
            {profile.latest_archetype?.primary_archetype || '--'}
          </p>
          <p className="text-xs text-text-muted">Archetype</p>
        </Card>
      </div>

      {/* Big Five Radar */}
      {bf && (
        <Card title="Big Five Personality Radar">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#1a2332" />
                <PolarAngleAxis dataKey="trait" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <Radar
                  dataKey="value"
                  stroke="#C9944A"
                  fill="#C9944A"
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4">
            {Object.entries(bf).map(([trait, val]) => (
              <TraitBar
                key={trait}
                label={trait.charAt(0).toUpperCase() + trait.slice(1)}
                value={val}
                color={TRAIT_COLORS[trait]}
              />
            ))}
          </div>
        </Card>
      )}

      {/* Archetype */}
      {profile.latest_archetype && (
        <Card title="Latest Archetype">
          <div className="flex items-center gap-4">
            <div>
              <p className="text-sm text-text-muted">Primary</p>
              <p className="text-xl font-bold text-gold">
                {profile.latest_archetype.primary_archetype}
              </p>
            </div>
            <div>
              <p className="text-sm text-text-muted">Shadow</p>
              <p className="text-xl font-bold text-purple">
                {profile.latest_archetype.shadow_archetype}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Consciousness */}
      {profile.latest_consciousness && (
        <Card title="Consciousness Level">
          <div className="flex items-center gap-4">
            <span className="text-4xl font-bold text-purple">
              {profile.latest_consciousness.level}
            </span>
            <span className="text-lg text-text-secondary">
              {profile.latest_consciousness.level_name}
            </span>
          </div>
        </Card>
      )}

      {/* Journal themes */}
      {profile.journal_themes && profile.journal_themes.length > 0 && (
        <Card title="Journal Themes">
          <div className="flex flex-wrap gap-2">
            {profile.journal_themes.map(t => (
              <span key={t} className="rounded-full bg-teal-dim px-3 py-1 text-sm text-teal">
                {t}
              </span>
            ))}
          </div>
        </Card>
      )}

      {!bf && !profile.latest_archetype && !profile.latest_consciousness && (
        <Card>
          <p className="text-center text-text-muted py-8">
            Complete your first assessment to see your profile here.
          </p>
        </Card>
      )}
    </div>
  )
}

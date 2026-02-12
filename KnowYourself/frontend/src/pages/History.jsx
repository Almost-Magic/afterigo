import { useEffect, useState } from 'react'
import { getHistory } from '../api'
import Card from '../components/Card'
import Loading from '../components/Loading'

const TYPE_LABELS = {
  big_five: 'Big Five',
  archetype: 'Archetype',
  consciousness: 'Consciousness',
}

const TYPE_COLOURS = {
  big_five: 'text-gold border-gold',
  archetype: 'text-teal border-teal',
  consciousness: 'text-purple border-purple',
}

export default function History() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getHistory()
      .then(setItems)
      .catch(e => { setError(e.message); setLoading(false) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loading text="Loading history..." />
  if (error) return <p className="text-rose">{error}</p>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Assessment History</h1>
        <p className="mt-1 text-text-secondary">
          {items.length} assessment{items.length !== 1 ? 's' : ''} completed
        </p>
      </div>

      {items.length === 0 ? (
        <Card>
          <p className="text-center text-text-muted py-8">
            No assessments yet. Take your first assessment to see your history here.
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {items.map(item => (
            <Card key={item.id} className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <span className={`rounded-lg border px-2 py-1 text-xs font-mono ${TYPE_COLOURS[item.assessment_type] || ''}`}>
                  {TYPE_LABELS[item.assessment_type] || item.assessment_type}
                </span>
                <span className="text-sm text-text-muted">
                  {new Date(item.created_at).toLocaleDateString('en-AU', {
                    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
                  })}
                </span>
              </div>
              <div className="text-sm text-text-secondary">
                {item.assessment_type === 'big_five' && item.scores && (
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(item.scores).map(([k, v]) => (
                      <span key={k} className="font-mono">
                        {k.charAt(0).toUpperCase()}: {Math.round(v)}
                      </span>
                    ))}
                  </div>
                )}
                {item.assessment_type === 'archetype' && item.scores?.primary_archetype && (
                  <span>{item.scores.primary_archetype}</span>
                )}
                {item.assessment_type === 'consciousness' && item.scores?.level && (
                  <span>{item.scores.level} ({item.scores.level_name})</span>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

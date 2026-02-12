import { useEffect, useState } from 'react'
import { getQuestionsConsciousness, submitConsciousness } from '../api'
import Card from '../components/Card'
import Loading from '../components/Loading'
import LikertScale from '../components/LikertScale'

const LEVEL_COLOURS = {
  Shame: '#6b7280', Guilt: '#6b7280', Apathy: '#6b7280', Grief: '#6b7280',
  Fear: '#ef4444', Desire: '#f59e0b', Anger: '#ef4444', Pride: '#f59e0b',
  Courage: '#22c55e', Neutrality: '#22c55e', Willingness: '#22c55e',
  Acceptance: '#14b8a6', Reason: '#3b82f6', Love: '#a855f7',
  Joy: '#a855f7', Peace: '#8b5cf6', Enlightenment: '#c9944a',
}

export default function Consciousness() {
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getQuestionsConsciousness()
      .then(data => {
        setQuestions(data.questions)
        setAnswers(new Array(data.total).fill(0))
        setLoading(false)
      })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [])

  function setAnswer(idx, val) {
    setAnswers(prev => { const n = [...prev]; n[idx] = val; return n })
  }

  async function handleSubmit() {
    if (answers.some(a => a === 0)) {
      setError('Please answer all 10 questions')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      const res = await submitConsciousness(answers)
      setResult(res)
    } catch (e) {
      setError(e.message)
    }
    setSubmitting(false)
  }

  if (loading) return <Loading text="Loading consciousness questions..." />

  if (result) {
    const colour = LEVEL_COLOURS[result.level_name] || '#c9944a'
    const pct = Math.min(100, (result.level / 700) * 100)
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-text-primary">Your Consciousness Level</h1>

        <Card className="text-center">
          <div className="relative mx-auto h-48 w-48">
            <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
              <circle cx="50" cy="50" r="42" fill="none" stroke="#1a2332" strokeWidth="8" />
              <circle
                cx="50" cy="50" r="42" fill="none"
                stroke={colour} strokeWidth="8"
                strokeDasharray={`${pct * 2.64} 264`}
                strokeLinecap="round"
                className="transition-all duration-1000"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold" style={{ color: colour }}>{result.level}</span>
              <span className="text-sm text-text-muted">/ 700+</span>
            </div>
          </div>
          <p className="mt-4 text-xl font-semibold" style={{ color: colour }}>{result.level_name}</p>
        </Card>

        {/* Scale reference */}
        <Card title="Hawkins Scale Reference">
          <div className="space-y-1 text-sm">
            {[
              [700, 'Enlightenment'], [600, 'Peace'], [540, 'Joy'], [500, 'Love'],
              [400, 'Reason'], [350, 'Acceptance'], [310, 'Willingness'],
              [250, 'Neutrality'], [200, 'Courage'], [175, 'Pride'],
              [150, 'Anger'], [125, 'Desire'], [100, 'Fear'], [75, 'Grief'],
              [50, 'Apathy'], [30, 'Guilt'], [20, 'Shame'],
            ].map(([lvl, name]) => (
              <div key={lvl} className="flex items-center gap-2">
                <span className="w-12 text-right font-mono text-text-muted">{lvl}</span>
                <div
                  className={`h-1 rounded ${result.level >= lvl ? 'opacity-100' : 'opacity-20'}`}
                  style={{ width: `${Math.max(10, lvl / 7)}%`, backgroundColor: LEVEL_COLOURS[name] || '#666' }}
                />
                <span className={result.level_name === name ? 'font-bold text-text-primary' : 'text-text-muted'}>
                  {name}
                </span>
              </div>
            ))}
          </div>
        </Card>

        {result.ai_interpretation && (
          <Card title="AI Reflection">
            <p className="whitespace-pre-wrap text-text-secondary leading-relaxed">
              {result.ai_interpretation}
            </p>
          </Card>
        )}

        <button
          onClick={() => { setResult(null); setAnswers(new Array(10).fill(0)) }}
          className="rounded-lg border border-border px-4 py-2 text-sm text-text-secondary hover:text-gold hover:border-gold transition-colors"
        >
          Take Again
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Consciousness Level Assessment</h1>
        <p className="mt-1 text-text-secondary">
          10 items inspired by David Hawkins' Map of Consciousness. Rate how true each statement is for you right now.
        </p>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-4">
        <div className="h-2 flex-1 rounded-full bg-midnight">
          <div
            className="h-full rounded-full bg-purple transition-all"
            style={{ width: `${(answers.filter(a => a > 0).length / 10) * 100}%` }}
          />
        </div>
        <span className="text-sm font-mono text-text-muted">
          {answers.filter(a => a > 0).length}/10
        </span>
      </div>

      <Card>
        <div className="space-y-6">
          {questions.map((q, i) => (
            <div key={i} className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-text-primary flex-1">
                <span className="mr-2 font-mono text-text-muted">{i + 1}.</span>
                {q.text}
              </p>
              <LikertScale value={answers[i]} onChange={setAnswer} questionIndex={i} />
            </div>
          ))}
        </div>
      </Card>

      <div className="flex justify-end">
        <button
          onClick={handleSubmit}
          disabled={submitting || answers.some(a => a === 0)}
          className="rounded-lg bg-gold px-6 py-2 text-sm font-medium text-midnight hover:bg-gold-light disabled:opacity-50 transition-colors"
        >
          {submitting ? 'Analysing...' : 'Submit Assessment'}
        </button>
      </div>

      {error && <p className="text-sm text-rose">{error}</p>}
    </div>
  )
}

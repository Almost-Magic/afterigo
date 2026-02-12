import { useEffect, useState } from 'react'
import { getQuestionsArchetype, submitArchetype } from '../api'
import Card from '../components/Card'
import Loading from '../components/Loading'

export default function Archetype() {
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    getQuestionsArchetype()
      .then(data => {
        setQuestions(data.questions)
        setAnswers(new Array(data.total).fill(''))
        setLoading(false)
      })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [])

  function choose(val) {
    const newAnswers = [...answers]
    newAnswers[current] = val
    setAnswers(newAnswers)
    if (current < questions.length - 1) {
      setCurrent(c => c + 1)
    }
  }

  async function handleSubmit() {
    if (answers.some(a => !a)) {
      setError('Please answer all questions')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      const res = await submitArchetype(answers)
      setResult(res)
    } catch (e) {
      setError(e.message)
    }
    setSubmitting(false)
  }

  if (loading) return <Loading text="Loading archetype questions..." />

  if (result) {
    const sorted = Object.entries(result.percentages).sort((a, b) => b[1] - a[1])
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-text-primary">Your Archetype Results</h1>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Card className="border-l-4 border-gold">
            <p className="text-sm text-text-muted">Primary Archetype</p>
            <p className="text-2xl font-bold text-gold">{result.primary_archetype}</p>
          </Card>
          <Card className="border-l-4 border-purple">
            <p className="text-sm text-text-muted">Shadow Archetype</p>
            <p className="text-2xl font-bold text-purple">{result.shadow_archetype}</p>
          </Card>
        </div>

        <Card title="All Archetypes">
          <div className="space-y-2">
            {sorted.map(([name, pct]) => (
              <div key={name} className="flex items-center gap-3">
                <span className="w-28 text-sm text-text-secondary">{name}</span>
                <div className="h-2 flex-1 rounded-full bg-midnight">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      name === result.primary_archetype ? 'bg-gold' :
                      name === result.shadow_archetype ? 'bg-purple' : 'bg-teal'
                    }`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className="w-10 text-right font-mono text-sm text-text-muted">{pct}%</span>
              </div>
            ))}
          </div>
        </Card>

        {result.ai_interpretation && (
          <Card title="AI Interpretation">
            <p className="whitespace-pre-wrap text-text-secondary leading-relaxed">
              {result.ai_interpretation}
            </p>
          </Card>
        )}

        <button
          onClick={() => { setResult(null); setAnswers(new Array(24).fill('')); setCurrent(0) }}
          className="rounded-lg border border-border px-4 py-2 text-sm text-text-secondary hover:text-gold hover:border-gold transition-colors"
        >
          Take Again
        </button>
      </div>
    )
  }

  const q = questions[current]
  if (!q) return null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Jungian Archetype Assessment</h1>
        <p className="mt-1 text-text-secondary">
          24 forced-choice questions. Choose the option that resonates more with you.
        </p>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-4">
        <div className="h-2 flex-1 rounded-full bg-midnight">
          <div
            className="h-full rounded-full bg-teal transition-all"
            style={{ width: `${(answers.filter(a => a).length / 24) * 100}%` }}
          />
        </div>
        <span className="text-sm font-mono text-text-muted">
          {answers.filter(a => a).length}/24
        </span>
      </div>

      <Card>
        <p className="mb-2 text-sm text-text-muted">Question {current + 1} of {questions.length}</p>
        <p className="mb-6 text-lg text-text-primary">Which statement resonates more with you?</p>
        <div className="flex flex-col gap-3">
          <button
            onClick={() => choose('a')}
            className={`rounded-xl border p-4 text-left transition-all ${
              answers[current] === 'a'
                ? 'border-gold bg-gold-dim text-gold'
                : 'border-border text-text-secondary hover:border-gold/50'
            }`}
          >
            <span className="mr-2 font-mono text-sm">A.</span> {q.a}
          </button>
          <button
            onClick={() => choose('b')}
            className={`rounded-xl border p-4 text-left transition-all ${
              answers[current] === 'b'
                ? 'border-teal bg-teal-dim text-teal'
                : 'border-border text-text-secondary hover:border-teal/50'
            }`}
          >
            <span className="mr-2 font-mono text-sm">B.</span> {q.b}
          </button>
        </div>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrent(c => Math.max(0, c - 1))}
          disabled={current === 0}
          className="rounded-lg border border-border px-4 py-2 text-sm text-text-secondary hover:text-gold disabled:opacity-30 transition-colors"
        >
          Previous
        </button>
        {current === questions.length - 1 && answers.every(a => a) ? (
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="rounded-lg bg-gold px-6 py-2 text-sm font-medium text-midnight hover:bg-gold-light disabled:opacity-50 transition-colors"
          >
            {submitting ? 'Analysing...' : 'Submit Assessment'}
          </button>
        ) : (
          <button
            onClick={() => setCurrent(c => Math.min(questions.length - 1, c + 1))}
            disabled={current === questions.length - 1}
            className="rounded-lg border border-border px-4 py-2 text-sm text-text-secondary hover:text-gold disabled:opacity-30 transition-colors"
          >
            Next
          </button>
        )}
      </div>

      {error && <p className="text-sm text-rose">{error}</p>}
    </div>
  )
}

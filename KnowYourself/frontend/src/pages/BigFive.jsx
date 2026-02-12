import { useEffect, useState } from 'react'
import { getQuestionsBigFive, submitBigFive } from '../api'
import Card from '../components/Card'
import Loading from '../components/Loading'
import LikertScale from '../components/LikertScale'
import TraitBar from '../components/TraitBar'

const TRAIT_COLORS = {
  openness: 'bg-purple',
  conscientiousness: 'bg-teal',
  extraversion: 'bg-gold',
  agreeableness: 'bg-green',
  neuroticism: 'bg-rose',
}

export default function BigFive() {
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(0)
  const PER_PAGE = 10

  useEffect(() => {
    getQuestionsBigFive()
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
      setError('Please answer all 50 questions')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      const res = await submitBigFive(answers)
      setResult(res)
    } catch (e) {
      setError(e.message)
    }
    setSubmitting(false)
  }

  if (loading) return <Loading text="Loading questions..." />

  if (result) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-text-primary">Your Big Five Results</h1>
        <Card title="Personality Scores">
          {Object.entries(result.scores).map(([trait, val]) => (
            <TraitBar
              key={trait}
              label={trait.charAt(0).toUpperCase() + trait.slice(1)}
              value={val}
              color={TRAIT_COLORS[trait] || 'bg-gold'}
            />
          ))}
        </Card>
        {result.ai_interpretation && (
          <Card title="AI Interpretation">
            <p className="whitespace-pre-wrap text-text-secondary leading-relaxed">
              {result.ai_interpretation}
            </p>
          </Card>
        )}
        <button
          onClick={() => { setResult(null); setAnswers(new Array(50).fill(0)); setPage(0) }}
          className="rounded-lg border border-border px-4 py-2 text-sm text-text-secondary hover:text-gold hover:border-gold transition-colors"
        >
          Take Again
        </button>
      </div>
    )
  }

  const pageQuestions = questions.slice(page * PER_PAGE, (page + 1) * PER_PAGE)
  const totalPages = Math.ceil(questions.length / PER_PAGE)
  const answeredOnPage = answers.slice(page * PER_PAGE, (page + 1) * PER_PAGE).filter(a => a > 0).length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Big Five Personality Assessment</h1>
        <p className="mt-1 text-text-secondary">
          50 items from the IPIP-NEO-PI inventory. Rate how accurately each statement describes you.
        </p>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-4">
        <div className="h-2 flex-1 rounded-full bg-midnight">
          <div
            className="h-full rounded-full bg-gold transition-all"
            style={{ width: `${(answers.filter(a => a > 0).length / 50) * 100}%` }}
          />
        </div>
        <span className="text-sm font-mono text-text-muted">
          {answers.filter(a => a > 0).length}/50
        </span>
      </div>

      <Card>
        <div className="space-y-6">
          {pageQuestions.map((q, i) => {
            const idx = page * PER_PAGE + i
            return (
              <div key={idx} className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm text-text-primary flex-1">
                  <span className="mr-2 font-mono text-text-muted">{idx + 1}.</span>
                  {q.text}
                </p>
                <LikertScale value={answers[idx]} onChange={setAnswer} questionIndex={idx} />
              </div>
            )
          })}
        </div>
      </Card>

      {/* Pagination + Submit */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setPage(p => Math.max(0, p - 1))}
          disabled={page === 0}
          className="rounded-lg border border-border px-4 py-2 text-sm text-text-secondary hover:text-gold disabled:opacity-30 transition-colors"
        >
          Previous
        </button>
        <span className="text-sm text-text-muted">Page {page + 1} of {totalPages}</span>
        {page < totalPages - 1 ? (
          <button
            onClick={() => setPage(p => p + 1)}
            className="rounded-lg border border-border px-4 py-2 text-sm text-text-secondary hover:text-gold transition-colors"
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="rounded-lg bg-gold px-6 py-2 text-sm font-medium text-midnight hover:bg-gold-light disabled:opacity-50 transition-colors"
          >
            {submitting ? 'Analysing...' : 'Submit Assessment'}
          </button>
        )}
      </div>

      {error && <p className="text-sm text-rose">{error}</p>}
    </div>
  )
}

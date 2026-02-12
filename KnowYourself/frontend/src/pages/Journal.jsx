import { useEffect, useState } from 'react'
import { getDailyPrompt, submitJournal } from '../api'
import Card from '../components/Card'
import Loading from '../components/Loading'

export default function Journal() {
  const [prompts, setPrompts] = useState([])
  const [selectedPrompt, setSelectedPrompt] = useState('')
  const [entry, setEntry] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getDailyPrompt()
      .then(data => {
        setPrompts(data.all_prompts)
        setSelectedPrompt(data.prompt)
        setLoading(false)
      })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [])

  async function handleSubmit() {
    if (!entry.trim()) {
      setError('Please write something first')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      const res = await submitJournal(selectedPrompt, entry)
      setResult(res)
    } catch (e) {
      setError(e.message)
    }
    setSubmitting(false)
  }

  if (loading) return <Loading text="Loading today's prompt..." />

  if (result) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-text-primary">Journal Entry Saved</h1>

        <Card className="border-l-4 border-gold">
          <p className="text-sm text-text-muted mb-1">Prompt</p>
          <p className="text-gold italic">"{result.prompt}"</p>
        </Card>

        <Card title="Your Entry">
          <p className="whitespace-pre-wrap text-text-secondary">{result.entry_text}</p>
        </Card>

        {result.ai_reflection && (
          <Card title="AI Reflection">
            <p className="whitespace-pre-wrap text-text-secondary leading-relaxed">
              {result.ai_reflection}
            </p>
          </Card>
        )}

        {result.themes && result.themes.length > 0 && (
          <Card title="Themes Detected">
            <div className="flex flex-wrap gap-2">
              {result.themes.map(t => (
                <span key={t} className="rounded-full bg-purple-dim px-3 py-1 text-sm text-purple">
                  {t}
                </span>
              ))}
            </div>
          </Card>
        )}

        <button
          onClick={() => { setResult(null); setEntry('') }}
          className="rounded-lg border border-border px-4 py-2 text-sm text-text-secondary hover:text-gold hover:border-gold transition-colors"
        >
          Write Another Entry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Daily Self-Inquiry Journal</h1>
        <p className="mt-1 text-text-secondary">
          Respond to a prompt. An AI guide will reflect back what it notices.
        </p>
      </div>

      <Card>
        <label className="mb-2 block text-sm text-text-muted">Select a prompt</label>
        <select
          value={selectedPrompt}
          onChange={e => setSelectedPrompt(e.target.value)}
          className="w-full rounded-lg border border-border bg-midnight px-3 py-2 text-text-primary focus:border-gold focus:outline-none"
        >
          {prompts.map(p => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </Card>

      <Card>
        <p className="mb-3 text-lg italic text-gold">"{selectedPrompt}"</p>
        <textarea
          value={entry}
          onChange={e => setEntry(e.target.value)}
          placeholder="Write your reflection here..."
          rows={10}
          maxLength={10000}
          className="w-full rounded-lg border border-border bg-midnight px-4 py-3 text-text-primary placeholder-text-muted focus:border-gold focus:outline-none resize-y"
        />
        <div className="mt-1 flex justify-between text-xs text-text-muted">
          <span>{entry.length.toLocaleString()} / 10,000</span>
          <span>Minimum: a few sentences</span>
        </div>
      </Card>

      <div className="flex justify-end">
        <button
          onClick={handleSubmit}
          disabled={submitting || !entry.trim()}
          className="rounded-lg bg-gold px-6 py-2 text-sm font-medium text-midnight hover:bg-gold-light disabled:opacity-50 transition-colors"
        >
          {submitting ? 'Reflecting...' : 'Submit & Get Reflection'}
        </button>
      </div>

      {error && <p className="text-sm text-rose">{error}</p>}
    </div>
  )
}

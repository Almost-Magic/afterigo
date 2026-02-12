const BASE = ''  // relative URLs — Vite proxy handles /api

async function request(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

// Questions
export const getQuestionsBigFive = () => request('/api/questions/big-five')
export const getQuestionsArchetype = () => request('/api/questions/archetype')
export const getQuestionsConsciousness = () => request('/api/questions/consciousness')
export const getDailyPrompt = () => request('/api/questions/daily-prompt')

// Assessments
export const submitBigFive = (answers) =>
  request('/api/assessments/big-five', { method: 'POST', body: JSON.stringify({ answers }) })
export const submitArchetype = (answers) =>
  request('/api/assessments/archetype', { method: 'POST', body: JSON.stringify({ answers }) })
export const submitConsciousness = (answers) =>
  request('/api/assessments/consciousness', { method: 'POST', body: JSON.stringify({ answers }) })

// Journal
export const submitJournal = (prompt, entry_text) =>
  request('/api/journal', { method: 'POST', body: JSON.stringify({ prompt, entry_text }) })

// History & Profile
export const getHistory = () => request('/api/history')
export const getProfile = () => request('/api/profile')
export const getHealth = () => request('/api/health')

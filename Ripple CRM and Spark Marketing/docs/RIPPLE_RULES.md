# RIPPLE_RULES.md — Operating Rules for Ripple CRM
## For: Claude Code
## Project: Ripple CRM v3 — Almost Magic Tech Lab
## Last Updated: February 2026

---

## WHO DOES WHAT

- **Claude Code (you)** builds and fixes Ripple. You are the operational agent.
- **Thalaiva** is the strategic advisor who wrote the specs. You do NOT call Thalaiva. Mani consults Thalaiva separately when strategic decisions are needed.
- **Mani** is the Curator, architect, and boss. He is NOT a developer. He is a strategist and builder who creates with AI assistance.
- If you hit an architectural question the spec doesn't answer, **ask Mani — don't guess.**

---

## AI USAGE — CRITICAL, NON-NEGOTIABLE

- **Ollama only** for all programmatic AI (embeddings, scoring, analysis, NLP). Route through Supervisor (:9000).
- **NEVER use cloud AI APIs.** No OpenAI API, no Anthropic API, no Google AI API. No `ANTHROPIC_API_KEY`, no `OPENAI_API_KEY`, no per-token charges. Ever.
- Browser subscriptions (Claude Max, ChatGPT) are for Mani's interactive use only — not for programmatic calls.
- If Ollama is down: auto-restart 3x via Supervisor, then ELAINE opens browser to claude.ai or ChatGPT. No silent cloud fallback.
- Remove any cloud fallback code if you encounter it.

---

## AMTL DESIGN SYSTEM — NON-NEGOTIABLE

| Token | Value |
|-------|-------|
| Dark mode background | `#0A0E14` (AMTL Midnight) |
| Surface colour | `#151B26` (Deep Navy) |
| Accent | `#C9944A` (Gold) |
| Light mode | Swaps to Neutral 50–200 backgrounds |
| Heading font | Sora (Google Fonts) |
| Body font | Inter |
| Code font | JetBrains Mono |
| Default theme | **Dark mode** |
| Theme toggle | **Must have** — dark/light toggle in header |

- Design philosophy: Calm, not exciting. Quietly powerful. NOT "sci-fi cockpits."
- Attribution footer: `Made with ❤️ by Mani Padisetti @ Almost Magic Tech Lab`

---

## DEVELOPMENT STANDARDS

1. **Australian English spelling** throughout (colour, favour, organise, defence)
2. **Before ANY solution:** Check if open-source tools can do it first
3. **Every app MUST have:** Beast tests, Proof/Playwright verification, GitHub push to Almost-Magic org, README + User Manual. **NEVER SKIP.**
4. **Error prevention:** Input validation on every user input. Error handling for all API calls. Clear error messages with recovery steps.
5. **Security:** Never commit secrets/API keys (.env files). Parameterised queries. Rate limiting. CORS config.
6. **Monitoring:** Health check endpoints. Contextual error logging.
7. **Licence:** MIT
8. **Preferred stack:** Python (FastAPI for Ripple), PostgreSQL (pgvector on port 5433), React + Vite + Tailwind (frontend), Docker

---

## RIPPLE-SPECIFIC CONFIGURATION

| Component | Port | Notes |
|-----------|------|-------|
| Ripple Backend | 8100 | FastAPI |
| Ripple Frontend | 3100 | React + Vite |
| PostgreSQL (pgvector) | 5433 | Shared Docker container, database name: `ripple` |
| Redis | 6379 | Cache/queue |
| Ollama | 11434 | Local LLM inference |
| The Workshop | 5003 | Register Ripple here with favicon |

---

## BUILD APPROACH

- **Layer by layer.** Do NOT build everything at once.
- Complete each step fully before moving to the next.
- Stop after each step and show Mani what you've done.
- Ask before creating files outside the Ripple project folder.
- When in doubt, ask Mani. Don't guess.

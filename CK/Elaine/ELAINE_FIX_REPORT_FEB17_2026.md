# ELAINE v4 — Fix Report
## 17 February 2026

---

### Fixes Applied

#### 1. BUG FIX: "open Claude desktop" message (Priority #1)
**File:** `api_routes_chat.py` line 308
**Was:** `"AI engine offline — open Claude desktop."`
**Now:** `"I can't reach any AI engine right now. Claude CLI and Ollama are both offline."`
**Rule:** ELAINE handles AI routing SILENTLY. She never asks the user to open anything.

#### 2. BUG FIX: AI Engine — added Ollama fallback (Priority #1)
**File:** `utils/ai_engine.py` (rewritten)
**Was:** Claude CLI only. No fallback. Returned None on failure.
**Now:** Claude CLI (primary) -> Ollama via Supervisor:9000 (fallback) -> Ollama direct:11434 -> None
**Added:** `_try_ollama()` function, `_is_ollama_available()` check, `check_ai_status()` now reports both engines.
**Key functions:** `query_ai()`, `query_ai_json()`, `check_ai_status()`

#### 3. BUG FIX: Voice Engine — ElevenLabs with fallback chain (Priority #2)
**File:** `utils/voice_engine.py` (NEW)
**Created:** Shared voice engine with fallback: ElevenLabs (PRIMARY) -> pyttsx3 (last resort)
**Voice ID:** `XQanfahzbl1YiUlZi5NW` (non-negotiable)
**Model:** `eleven_flash_v2_5` (fastest)
**Added:** Placeholder API key detection — warns if key is `sk_your_*`
**Key functions:** `speak()`, `get_voice_status()`

#### 4. FIX: TTS endpoints now use shared voice engine
**File:** `api_routes_chat.py` (updated TTS routes)
**Was:** `/api/tts` used raw urllib to hit ElevenLabs. `/api/tts/status` had manual checks.
**Now:** Both use `utils/voice_engine.py`. Added `/api/voice/speak` and `/api/voice/engine-status` endpoints.

#### 5. NEW: Test Suite — 33 tests
**File:** `tests/test_elaine.py` (NEW)
**Coverage:** Health (3), Chat (5), Morning Brief (3), Thinking (3), Gatekeeper (3), Ecosystem (3), Voice (4), Dashboard (3), Tools (2), AI Engine (2), Voice Engine (2)
**Result:** 33/33 passing

---

### Test Results
```
33 passed in 32.00s

TestHealth:           3/3 PASS
TestChat:             5/5 PASS
TestMorningBrief:     3/3 PASS
TestThinking:         3/3 PASS
TestGatekeeper:       3/3 PASS
TestEcosystem:        3/3 PASS
TestVoice:            4/4 PASS
TestDashboard:        3/3 PASS
TestTools:            2/2 PASS
TestAIEngine:         2/2 PASS
TestVoiceEngine:      2/2 PASS
```

---

### Still Pending

1. **ElevenLabs API Key** — `.env` has placeholder `sk_your_key_here`. Mani needs to set the real key from https://elevenlabs.io/app/settings/api-keys. Without it, TTS falls back to browser voice / pyttsx3.

2. **Chat conversation history** — Currently stored in frontend (JavaScript array). Not yet persisted to SQLite per session. The chat works and returns real AI responses, but history is lost on page reload.

3. **Gatekeeper AI classification** — Currently uses local rule-based checks (Sentinel + Compassion + Communication modules). Not yet wired to use AI for clear/review/hold classification. Works but is rule-based, not AI-driven.

4. **Thinking integration with Costanza** — Chat auto-routes thinking questions to the built-in ThinkingFrameworksEngine. Direct Costanza (port 5001) integration would require Costanza to be running and an HTTP call. Currently uses built-in fallback which works.

---

### Files Changed
```
Modified:
  api_routes_chat.py     — Fixed "open Claude desktop" bug, rewired TTS to voice engine
  utils/ai_engine.py     — Added Ollama fallback, improved status reporting

Created:
  utils/voice_engine.py  — Shared voice engine (ElevenLabs + pyttsx3 fallback)
  tests/__init__.py      — Test package init
  tests/test_elaine.py   — 33 Beast tests
  ELAINE_AUDIT_REPORT.md — Pre-fix audit
  ELAINE_FIX_REPORT_FEB17_2026.md — This file
```

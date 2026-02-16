# ELAINE v4 — Audit Report
## 17 February 2026

### Summary
ELAINE is a substantial 16-module Flask application at `CK/Elaine/` running on port 5000. The core architecture is sound — modules initialize cleanly, the dashboard renders correctly, and most endpoints return real data. Two critical bugs and one missing piece (tests) were identified.

---

### Feature-by-Feature Audit

| Feature | Status | Detail |
|---------|--------|--------|
| **Dashboard (GET /)** | WORKING | Dark theme default (#0A0E14), dark/light toggle in header, AMTL branding, Sora font, sidebar nav, card grid layout |
| **Health (GET /api/health)** | WORKING | Returns healthy status, Supervisor connectivity check |
| **Status (GET /api/status)** | WORKING | All 16 modules reported with counts |
| **Chat (POST /api/chat)** | BUG FIXED | Was saying "open Claude desktop" on AI failure (line 308). Now says "I can't reach any AI engine right now." |
| **AI Engine** | BUG FIXED | Was Claude CLI only with no fallback. Now: Claude CLI -> Ollama -> None |
| **TTS (POST /api/tts)** | BUG FIXED | Was hardcoded ElevenLabs only. Now uses voice_engine.py with fallback chain |
| **Voice Config (GET /api/voice/config)** | WORKING | Returns correct voice_id XQanfahzbl1YiUlZi5NW |
| **Voice Status (GET /api/tts/status)** | WORKING | Now uses shared voice_engine.py |
| **Voice Speak (POST /api/voice/speak)** | NEW | Added endpoint for direct TTS via voice engine |
| **ElevenLabs voice_id** | CORRECT | XQanfahzbl1YiUlZi5NW throughout (config.py, voice.py, .env) |
| **.env API Key** | WARNING | Set to placeholder `sk_your_key_here` — needs real key |
| **Morning Briefing (GET /api/morning-briefing)** | WORKING | Collects real module data, renders Jinja2 templates, sends to Ollama in background |
| **Morning Briefing Voice** | WORKING | Segments with emotional tags (warm, urgent, calm, etc.) |
| **Morning Briefing Scheduler** | WORKING | APScheduler: daily 7 AM AEST, weekly prep Mon 6:30 AM |
| **Ecosystem (GET /api/ecosystem)** | WORKING | Pings 11 apps concurrently (3s timeout), returns status per app |
| **Tool Registry (GET /api/tools)** | WORKING | 17 tools registered with health endpoints |
| **Tool Health (GET /api/tools/health)** | WORKING | Concurrent pinging with latency tracking |
| **Thinking Frameworks** | WORKING | Engine with analyse, matrix, history endpoints |
| **Gravity Field** | WORKING | Priority tracking with red giants, trust debt |
| **Constellation** | WORKING | POI tracking, network intelligence, reciprocity |
| **Cartographer** | WORKING | Territory mapping, discovery engine |
| **Amplifier** | WORKING | Content engine with thinking integration |
| **Sentinel** | WORKING | Trust engine with audit reviews |
| **Chronicle** | WORKING | Meeting intelligence with commitment tracking |
| **Innovator + Beast** | WORKING | Innovation detection and research briefs |
| **Learning Radar** | WORKING | Interest tracking and connections |
| **Communication** | WORKING | 7 communication frameworks |
| **Strategic** | WORKING | 8 strategic frameworks |
| **Compassion** | WORKING | Wellbeing monitoring |
| **Gatekeeper** | WORKING | Pre-transmission quality checks (local, no AI classification) |
| **Orchestrator** | WORKING | Wires all modules together with cascade logic |
| **Frustration Log** | WORKING | Append-only JSONL friction logging |
| **STT (POST /api/stt)** | WORKING | faster-whisper (if installed), CPU int8 |
| **Microphone (browser)** | WORKING | webkitSpeechRecognition + Whisper fallback |
| **Philosophy Research** | WORKING | Corpus search + Ollama synthesis |
| **Wisdom Quotes** | WORKING | Proxied to Wisdom Quotes API :3350 |
| **Tests** | WAS MISSING | Created 33 tests — all passing |

---

### Critical Issues Found

1. **BUG: "open Claude desktop"** — `api_routes_chat.py:308` returned "AI engine offline — open Claude desktop." when Claude CLI was unavailable. ELAINE should NEVER tell the user to open anything.

2. **BUG: No AI fallback** — `utils/ai_engine.py` was Claude CLI only. If Claude CLI failed, ELAINE had no backup. Ollama (via Supervisor on 9000) should be the fallback.

3. **BUG: Voice fallback chain missing** — The TTS endpoint used raw ElevenLabs via urllib. No fallback to pyttsx3. No shared voice engine module.

4. **WARNING: ElevenLabs API key is placeholder** — `.env` has `ELEVENLABS_API_KEY=sk_your_key_here`. This means all TTS will fall through to browser voice or pyttsx3 until Mani sets the real key.

5. **MISSING: Tests** — No test directory existed. Zero test coverage.

---

### What Was NOT Broken
The core app architecture is solid. All 16 modules initialize and work. The dashboard is beautiful. The voice personality system in `modules/chronicle/voice.py` is excellent. The ecosystem health checks work. The morning briefing collects real data from all modules. APScheduler runs on time.

---

### Honest Assessment
ELAINE is about 90% functional. The 10% that was broken was highly visible (voice, chat error message). The fixes are surgical — no architectural changes needed.

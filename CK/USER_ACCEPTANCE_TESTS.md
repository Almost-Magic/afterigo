# User Acceptance Tests — AMTL Ecosystem
## Manual Walkthrough Script for Mani
### Created: 13 February 2026

> **Purpose:** These are REAL user tests, not health checks. Each test simulates what a real user would actually do. If it fails here, it's broken for real.

---

## Pre-Requisites

Before starting, ensure:
1. Docker Desktop is running
2. Ollama is running (port 11434)
3. Run `.\services.ps1 start all` from Source and Brand directory
4. Wait 60 seconds for everything to boot

---

## 1. THE SUPERVISOR (Port 9000)

**URL:** http://localhost:9000

### Tests

- [ ] **1.1 — Health endpoint returns real data**
  - Open: http://localhost:9000/api/health
  - **Expected:** JSON response with service statuses, GPU info, uptime — NOT just `{"status": "ok"}`
  - **Look for:** VRAM usage numbers, list of registered services, model registry info

- [ ] **1.2 — Model registry loads**
  - Open: http://localhost:9000/api/models (or check health response for model list)
  - **Expected:** List of Ollama models (gemma2:27b, nomic-embed-text, etc.)
  - **Fail if:** Empty list or error

- [ ] **1.3 — LLM request actually works**
  - Open a terminal and run:
    ```
    curl -X POST http://localhost:9000/api/chat -H "Content-Type: application/json" -d "{\"prompt\": \"Say hello in exactly 5 words\", \"model\": \"gemma2:27b\"}"
    ```
  - **Expected:** A coherent 5-word response within 30 seconds
  - **Fail if:** Timeout, error, or empty response

- [ ] **1.4 — GPU status is accurate**
  - Open: http://localhost:9000/api/gpu (or health endpoint GPU section)
  - **Expected:** Shows VRAM usage that roughly matches `nvidia-smi` output
  - **Verify:** Run `nvidia-smi` in terminal and compare numbers

---

## 2. ELAINE — Chief of Staff (Port 5000)

**URL:** http://localhost:5000

### Tests

- [ ] **2.1 — Main UI loads with real content**
  - Open: http://localhost:5000
  - **Expected:** ELAINE chat interface loads. You see the chat input box, ELAINE branding, dark theme with AMTL Midnight background
  - **Fail if:** Blank page, error page, or just a health JSON

- [ ] **2.2 — Chat actually responds**
  - Type in the chat box: `What can you help me with?`
  - Press Enter/Send
  - **Expected:** ELAINE responds with a coherent answer describing her capabilities within 15 seconds
  - **Fail if:** Spinner hangs forever, error message, or no response after 30 seconds

- [ ] **2.3 — Chat uses Ollama (not hardcoded responses)**
  - Type: `What is the capital of France?`
  - **Expected:** "Paris" — a real LLM response, not a canned answer
  - **Fail if:** Generic "I can help with..." response that ignores your question

- [ ] **2.4 — Morning Brief loads with real data**
  - Navigate to Morning Brief section (look for briefing/morning brief link or tab)
  - **Expected:** Shows today's date, real briefing content (tasks, weather, calendar items, or at minimum a "no data" message that explains why)
  - **Fail if:** 404 error, blank section, or crashes

- [ ] **2.5 — Voice status is clear**
  - Look for voice/audio controls in the UI
  - **Expected:** Either voice works (you hear ELAINE speak) OR there's a clear message like "Voice unavailable — ElevenLabs API key not configured"
  - **Fail if:** Silent failure with no explanation

- [ ] **2.6 — Dark/Light theme toggle exists and works**
  - Find the theme toggle (usually in header)
  - Click it
  - **Expected:** Theme switches between dark (AMTL Midnight #0A0E14) and light mode
  - **Fail if:** No toggle exists, or toggle does nothing

---

## 3. ELAINE DESKTOP (Electron App)

### Tests

- [ ] **3.1 — Desktop app launches**
  - Navigate to `CK/Elaine/elaine-desktop/` in terminal
  - Run: `npm start` (or the appropriate launch command)
  - **Expected:** Electron window opens showing ELAINE UI
  - **Fail if:** Crash on launch, white screen, or "cannot connect" error

- [ ] **3.2 — Desktop app connects to backend**
  - Once launched, try typing a message in the chat
  - **Expected:** Same functionality as web version — chat responds
  - **Fail if:** "Connection refused" or perpetual loading

---

## 4. THE WORKSHOP — Mission Control (Port 5003)

**URL:** http://localhost:5003

### Tests

- [ ] **4.1 — Main dashboard loads**
  - Open: http://localhost:5003
  - **Expected:** Workshop dashboard with service cards/tiles for all AMTL apps
  - **Fail if:** Blank page, error, or just health JSON

- [ ] **4.2 — All app cards are visible**
  - Scroll through the dashboard
  - **Expected:** Cards for at minimum: ELAINE, Costanza, CK Writer, Learning Assistant, Genie, Peterman, Junk Drawer, Author Studio
  - **Count the cards and note how many:** ____
  - **Fail if:** Missing cards for known apps, or only 1-2 cards showing

- [ ] **4.3 — Health status indicators are live**
  - Look at each card's status indicator (green/red dot, or similar)
  - **Expected:** Running services show green/healthy. Stopped services show red/down. Statuses update when you refresh.
  - **Fail if:** All show same status regardless of actual state, or statuses never update

- [ ] **4.4 — Launch button works for ELAINE**
  - Find ELAINE's card and click its launch/open button
  - **Expected:** Opens ELAINE in a new tab at http://localhost:5000, or launches the app if not running
  - **Fail if:** Button does nothing, 404, or error

- [ ] **4.5 — Launch button works for CK Writer**
  - Find CK Writer's card and click its launch/open button
  - **Expected:** Opens CK Writer at http://localhost:5004
  - **Fail if:** Button does nothing or errors

- [ ] **4.6 — Launch button works for Genie**
  - Find Genie's card and click its launch/open button
  - **Expected:** Opens Genie at http://localhost:3000 (frontend) or http://localhost:8000
  - **Fail if:** Button does nothing or errors

- [ ] **4.7 — Dark/Light theme toggle**
  - Find and click the theme toggle
  - **Expected:** Theme switches properly
  - **Fail if:** No toggle, or visual glitches on switch

---

## 5. CK WRITER (Port 5004)

**URL:** http://localhost:5004

### Tests

- [ ] **5.1 — UI loads completely**
  - Open: http://localhost:5004
  - **Expected:** Writing interface loads with editor area, document list/sidebar, and toolbar
  - **Fail if:** Blank page, error, or just JSON

- [ ] **5.2 — Can create a new document**
  - Click "New Document" (or equivalent button)
  - Type a title: "Test Document UAT"
  - Type some body text: "This is a user acceptance test."
  - Save the document
  - **Expected:** Document saves without error. Appears in document list.
  - **Fail if:** Save fails, error on creation, or document doesn't appear in list

- [ ] **5.3 — Can reopen a saved document**
  - Click on "Test Document UAT" in the document list
  - **Expected:** Document opens with the text you typed
  - **Fail if:** Document is empty, wrong content, or fails to open

- [ ] **5.4 — AI writing assistance works**
  - Use any AI-powered feature (grammar check, rewrite, suggest, etc.)
  - **Expected:** Gets a response from Ollama via Supervisor within 15 seconds
  - **Fail if:** Feature is missing, hangs, or returns an error about Ollama/Supervisor connection

- [ ] **5.5 — Dark/Light theme toggle**
  - Toggle theme
  - **Expected:** Clean switch between dark and light mode

---

## 6. COSTANZA — Mental Models Engine (Port 5001)

**URL:** http://localhost:5001

### Tests

- [ ] **6.1 — API health responds**
  - Open: http://localhost:5001/api/health
  - **Expected:** JSON with status healthy, model count (should be ~166 models)

- [ ] **6.2 — Models endpoint returns frameworks**
  - Open: http://localhost:5001/api/models
  - **Expected:** JSON listing mental models across 3 engines (Decision Intelligence, Communication, Strategic Analysis)
  - **Fail if:** Empty list or error

- [ ] **6.3 — Analysis endpoint works**
  - Run in terminal:
    ```
    curl -X POST http://localhost:5001/api/analyze -H "Content-Type: application/json" -d "{\"text\": \"Should I hire a new developer or outsource?\", \"engine\": \"decision\"}"
    ```
  - **Expected:** Returns analysis using one or more mental models
  - **Fail if:** Error or empty response

---

## 7. LEARNING ASSISTANT (Port 5002)

**URL:** http://localhost:5002

### Tests

- [ ] **7.1 — UI loads with tool panels**
  - Open: http://localhost:5002
  - **Expected:** Dashboard with learning tools visible (should have up to 37 tool panels)
  - **Fail if:** Blank page or error

- [ ] **7.2 — Can create a flashcard**
  - Find the Flashcards section
  - Create a new flashcard: Front = "What is AMTL?", Back = "Almost Magic Tech Lab"
  - Save it
  - **Expected:** Flashcard saves and appears in list
  - **Fail if:** Save fails or flashcard doesn't appear

- [ ] **7.3 — Can create a note**
  - Find the Notes section
  - Create a note: Title = "UAT Test Note", Content = "Testing the Learning Assistant"
  - Save it
  - **Expected:** Note saves and is retrievable

- [ ] **7.4 — AI features work**
  - Try any AI-powered feature (summarize, quiz generation, etc.)
  - **Expected:** Gets response from Ollama within 15 seconds
  - **Fail if:** Hangs or errors about AI connection

---

## 8. JUNK DRAWER (Port 5005/5006 backend, Port 3005 frontend)

**URL:** http://localhost:3005 (React frontend) or http://localhost:5005

### Tests

- [ ] **8.1 — Backend health**
  - Open: http://localhost:5005/api/health (or 5006)
  - **Expected:** JSON health response with scan status info

- [ ] **8.2 — Frontend loads**
  - Open: http://localhost:3005
  - **Expected:** File management dashboard showing scanned files, thermal scores, duplicate detection
  - **Fail if:** Blank page or connection refused

- [ ] **8.3 — File scan runs**
  - Trigger a scan (if there's a scan button) or check if files are listed
  - **Expected:** Shows files from configured scan directories with thermal scores
  - **Fail if:** Empty file list with no explanation

---

## 9. AUTHOR STUDIO (Port 5007)

**URL:** http://localhost:5007

### Tests

- [ ] **9.1 — UI loads**
  - Open: http://localhost:5007
  - **Expected:** Book authoring interface loads
  - **Fail if:** Blank page, error, or just JSON

- [ ] **9.2 — Can start a new project**
  - Look for "New Project" or similar
  - **Expected:** Can create a book/writing project
  - **Fail if:** Feature missing or errors

---

## 10. PETERMAN SEO (Port 5008)

**URL:** http://localhost:5008

### Tests

- [ ] **10.1 — UI loads with chambers**
  - Open: http://localhost:5008
  - **Expected:** Brand intelligence dashboard with chamber sections (brands, perception, authority, etc.)
  - **Fail if:** Blank page or error

- [ ] **10.2 — Can create/view a brand**
  - Navigate to Brands section
  - **Expected:** Can see brand list or create a new brand entry
  - **Fail if:** Feature broken or missing

- [ ] **10.3 — Search engine integration**
  - Try a search/analysis feature
  - **Expected:** Uses SearXNG (port 8888) to return results
  - **Fail if:** Search fails with connection error to SearXNG

---

## 11. GENIE — AI Bookkeeper (Backend 8000, Frontend 3000)

**URL:** http://localhost:3000 (frontend) | http://localhost:8000 (API)

### Tests

- [ ] **11.1 — Backend health is detailed**
  - Open: http://localhost:8000/api/health
  - **Expected:** JSON with database status, module count, version info — not just `{"status": "ok"}`

- [ ] **11.2 — Frontend loads with dashboard**
  - Open: http://localhost:3000
  - **Expected:** Genie dashboard loads with navigation groups (Overview / Money / Intelligence / Reports & Export / Tools)
  - **Fail if:** Blank page, "Cannot connect to backend", or React error screen

- [ ] **11.3 — Dashboard shows real data**
  - Look at the main dashboard
  - **Expected:** Financial overview with numbers (even if $0.00), charts, or a clear "No data yet" message
  - **Fail if:** Empty widgets with no data and no explanation

- [ ] **11.4 — Can navigate to Invoices**
  - Click on Invoices in the navigation
  - **Expected:** Invoice list page loads (may be empty but functional)

- [ ] **11.5 — Can create an invoice**
  - Click "New Invoice" or equivalent
  - Fill in: Customer = "Test Customer", Amount = $100, Description = "UAT Test"
  - Save
  - **Expected:** Invoice saves and appears in list
  - **Fail if:** Save error, validation error with no guidance, or crash

- [ ] **11.6 — Can navigate to Transactions**
  - Click Transactions in nav
  - **Expected:** Transaction list loads

- [ ] **11.7 — Cash Flow page works**
  - Navigate to Cash Flow
  - **Expected:** Tab 0 (Overview) shows "Cash Position". Tab 1 (Forecast) shows "Current Cash"
  - **Fail if:** Crashes, blank, or tabs don't switch

- [ ] **11.8 — AI features work (Genie AI chat)**
  - Find the AI/Genie chat feature
  - Ask: "What are my total expenses?"
  - **Expected:** AI responds with an answer (even if "no data found") within 15 seconds
  - **Fail if:** Hangs, errors about Ollama, or no AI feature visible

- [ ] **11.9 — Dark/Light theme toggle**
  - Toggle theme
  - **Expected:** Clean dark (AMTL Midnight) / light switch

---

## 12. RIPPLE CRM (Backend 8100, Frontend 3100)

**URL:** http://localhost:3100 (frontend) | http://localhost:8100 (API)

### Tests

- [ ] **12.1 — Backend health**
  - Open: http://localhost:8100/api/health
  - **Expected:** JSON health response with database connection status

- [ ] **12.2 — Frontend loads**
  - Open: http://localhost:3100
  - **Expected:** Ripple CRM dashboard loads with navigation (Contacts, Companies, Deals, Pipeline, etc.)
  - **Fail if:** Blank page, React error, or "Cannot connect to API"

- [ ] **12.3 — Can create a contact**
  - Navigate to Contacts
  - Click "New Contact" or "Add Contact"
  - Fill in: Name = "Test Person", Email = "test@example.com"
  - Save
  - **Expected:** Contact saves and appears in contact list
  - **Fail if:** Save fails or contact doesn't appear

- [ ] **12.4 — Can view pipeline**
  - Navigate to Pipeline/Deals
  - **Expected:** Pipeline view loads (Kanban board or list of deal stages)
  - **Fail if:** Blank or error

- [ ] **12.5 — Can create a deal**
  - Click "New Deal" or equivalent
  - Fill in: Name = "Test Deal", Value = $10,000, Stage = first available
  - Save
  - **Expected:** Deal saves and appears in pipeline

---

## 13. TOUCHSTONE — Marketing Attribution (Backend 8200, Dashboard 3200)

**URL:** http://localhost:3200 (dashboard) | http://localhost:8200 (API)

### Tests

- [ ] **13.1 — Backend health**
  - Open: http://localhost:8200/api/v1/health
  - **Expected:** JSON health response

- [ ] **13.2 — Dashboard loads**
  - Open: http://localhost:3200
  - **Expected:** Attribution dashboard with charts (Recharts), even if showing "No data"
  - **Fail if:** Blank page or build error

---

## 14. DOCKER TOOLS

### n8n — Automation Engine (Port 5678)

- [ ] **14.1 — n8n login page loads**
  - Open: http://localhost:5678
  - **Expected:** n8n login page or dashboard (if already logged in)
  - **Credentials:** admin / almostmagic
  - **Fail if:** Connection refused or Docker container not running

- [ ] **14.2 — Can log in to n8n**
  - Enter credentials: admin / almostmagic
  - **Expected:** n8n workflow dashboard loads with existing workflows
  - **Fail if:** Login fails or redirects to error

- [ ] **14.3 — Workflows exist**
  - Look at the workflow list
  - **Expected:** At least health monitoring, Foreperson audit, and backup workflows exist
  - **Note how many workflows:** ____

### Listmonk — Email Campaigns (Port 9001)

- [ ] **14.4 — Listmonk UI loads**
  - Open: http://localhost:9001
  - **Expected:** Listmonk login page or dashboard
  - **Fail if:** Connection refused

- [ ] **14.5 — Can log in**
  - Use default credentials (listmonk / listmonk or as configured)
  - **Expected:** Listmonk dashboard with lists and campaigns sections

### SearXNG — Search (Port 8888)

- [ ] **14.6 — SearXNG loads**
  - Open: http://localhost:8888
  - **Expected:** SearXNG search page with search bar
  - **Fail if:** Connection refused

- [ ] **14.7 — Search actually works**
  - Type "Almost Magic Tech Lab" in the search bar and submit
  - **Expected:** Search results appear within 10 seconds
  - **Fail if:** No results, timeout, or error

### Ollama (Port 11434)

- [ ] **14.8 — Ollama responds**
  - Open: http://localhost:11434
  - **Expected:** "Ollama is running" message

- [ ] **14.9 — Ollama has models loaded**
  - Open: http://localhost:11434/api/tags
  - **Expected:** JSON listing available models (gemma2:27b, nomic-embed-text, etc.)
  - **Fail if:** Empty model list

### PostgreSQL / pgvector (Port 5433)

- [ ] **14.10 — PostgreSQL is accessible**
  - Run in terminal: `psql -h localhost -p 5433 -U postgres -c "SELECT 1;"` (or use Docker exec)
  - **Expected:** Returns `1`
  - **Fail if:** Connection refused

### Redis (Port 6379)

- [ ] **14.11 — Redis responds**
  - Run in terminal: `docker exec -it <redis-container> redis-cli ping`
  - **Expected:** `PONG`
  - **Fail if:** Connection refused or container not running

---

## 15. CROSS-APP INTEGRATION TESTS

- [ ] **15.1 — Workshop shows accurate health for all running services**
  - Open Workshop at http://localhost:5003
  - Cross-reference each card's status with actual service availability
  - **Expected:** Green = actually reachable. Red = actually down. No false positives.

- [ ] **15.2 — ELAINE can reach Supervisor**
  - In ELAINE chat, ask: "What is the Supervisor status?"
  - **Expected:** ELAINE queries the Supervisor and returns real status info

- [ ] **15.3 — All AI features route through Supervisor (not direct Ollama)**
  - Check ELAINE, CK Writer, Learning Assistant AI features
  - **Expected:** Requests go to port 9000 (Supervisor), not 11434 (Ollama directly)
  - **Verify:** Check Supervisor logs for incoming requests

---

## Score Sheet

| # | App | Tests Passed | Tests Failed | Notes |
|---|-----|-------------|-------------|-------|
| 1 | Supervisor | /4 | | |
| 2 | ELAINE | /6 | | |
| 3 | ELAINE Desktop | /2 | | |
| 4 | Workshop | /7 | | |
| 5 | CK Writer | /5 | | |
| 6 | Costanza | /3 | | |
| 7 | Learning Assistant | /4 | | |
| 8 | Junk Drawer | /3 | | |
| 9 | Author Studio | /2 | | |
| 10 | Peterman | /3 | | |
| 11 | Genie | /9 | | |
| 12 | Ripple CRM | /5 | | |
| 13 | Touchstone | /2 | | |
| 14 | Docker Tools | /11 | | |
| 15 | Integration | /3 | | |
| **TOTAL** | | **/69** | | |

**Date tested:** ________________
**Tested by:** ________________
**Overall verdict:** PASS / FAIL

---

*"We don't need more apps. We need the apps we have to actually work."*

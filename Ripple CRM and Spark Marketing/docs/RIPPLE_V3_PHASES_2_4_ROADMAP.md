# RIPPLE v3 — PHASES 2-4 ROADMAP
## Future Build Specifications (Save for Later)
**Date:** 12 February 2026  
**Author:** Thalaiva (Strategic Advisor) for Almost Magic Tech Lab  
**Status:** ROADMAP DOCUMENT — Do not build until Phase 1 is shipped and tested.

---

## HOW TO USE THIS DOCUMENT

This is the future phases roadmap for Ripple v3. It contains everything that was deliberately excluded from the Phase 1 Build Spec. When you're ready to build a phase, Thalaiva will convert the relevant section into an executable build spec like the Phase 1 document — with database schema, API routes, UI wireframes, and build order.

**Rule:** Do not start any phase until the previous phase passes the 5-Phase Completion Protocol including the 5-Day Use Test.

**Dependencies:** Each phase assumes the previous phase is complete and stable.

---

## PHASE OVERVIEW

| Phase | Name | Timeline | Prerequisite |
|-------|------|----------|-------------|
| **Phase 1** | Core Relationship OS | Now → 3 months | — (BUILD SPEC DELIVERED) |
| **Phase 2** | Intelligence & Communication | 3-6 months | Phase 1 passes 5-Day Use Test |
| **Phase 3** | Sales Force Automation | 6-12 months | Phase 2 stable + first patent filed |
| **Phase 4** | Advanced & Agentic | 12-24 months | Phase 3 stable + 100+ contacts in system |

---

# PHASE 2: INTELLIGENCE & COMMUNICATION LAYER
## Timeline: 3-6 Months After Phase 1

**Goal:** Make Ripple smart and connected. Email/calendar sync means Ripple becomes the system of record, not a side tool. Intelligence layer means Ripple tells you things you didn't know.

### 2.1 Email & Calendar Bidirectional Sync

**What it does:** Connects to Gmail / Outlook. Auto-logs all emails. Syncs calendar events. Ripple becomes the truth — not a place you manually update.

**Email Features:**
- Gmail sidebar Chrome extension: view contact record, log email, create deal without leaving Gmail
- Outlook add-in: same features for Outlook desktop and web
- Email tracking: opens, clicks, replies, forwards with real-time notification
- Auto-log: all emails with matched contacts (configurable: all / selected / none)
- Email templates with personalisation tokens and AI-generated suggestions
- Send-time optimisation: AI recommends best send time per contact based on historical open patterns
- Shared inbox support: team emails (sales@, info@) with assignment and routing

**Calendar Features:**
- Bidirectional sync: Google Calendar / Exchange. Two-way create/update/delete.
- Meeting scheduler: shareable booking link (built-in Calendly equivalent)
- Intentional Calendar: when meeting is created → "Which deal is this for? What outcome do you want?" Metadata survives round-trip sync
- Meeting Prep ("Prep Me"): auto-generate brief from contact history, deal status, recent comms, news
- Meeting Follow-Up ("Follow Me"): "Meeting with Sarah ended 5 min ago. Log notes? Create actions?"
- Round-robin booking: distribute meetings across team based on availability and capacity
- Timezone intelligence: auto-detect attendee timezones, warning if meeting outside business hours

**Technical notes:**
- Google Workspace API + Microsoft Graph API
- OAuth 2.0 for auth
- Webhook-based sync for near-real-time
- Email matching: match by email address to contacts table
- New endpoint group: `/api/email/*`, `/api/calendar/*`
- New tables: `email_messages`, `calendar_events`, `email_templates`

### 2.2 Meeting Intelligence Hub

**What it does:** Captures meeting context — notes, actions, commitments — especially for unrecorded meetings (the 80% nobody else serves).

**The Innovation (Unrecorded Meeting Intelligence):**
Most CRM meeting intelligence requires recording (Gong, Chorus, Fireflies). But most SMB meetings aren't recorded — informal, in-person, or customer refuses. Ripple focuses on the unrecorded majority.

**Features:**
- Pre-meeting: "Prep Me" brief (contact history, deal status, last meeting notes, suggested talking points)
- During meeting: lightweight note-taking interface with structured fields (attendees, topics, decisions, actions, commitments)
- Post-meeting: "Follow Me" prompt → guided note capture → auto-extract commitments → auto-create follow-up tasks
- For recorded meetings (opt-in): Transcription via Whisper (local), structured summary generation via Ollama, action item extraction, sentiment analysis
- Meeting analytics: frequency, duration, actions-created-to-completed ratio, meeting-to-close correlation

**Patent candidate:** "Unrecorded Meeting Intelligence with Structured Capture and Commitment Extraction" — 85% confidence.

**Technical notes:**
- Whisper integration (local, via Supervisor GPU scheduling)
- New tables: `meeting_notes`, `meeting_actions`
- Extends `activities` table with meeting-specific metadata
- Auto-creates `commitments` from extracted action items

### 2.3 Channel DNA v1

**What it does:** Auto-detects each contact's preferred communication channel and optimal timing from response patterns.

**How it works:**
- Track response latency by channel: email, phone, SMS, LinkedIn
- Track response rates by time-of-day and day-of-week
- Build per-contact profile: "Best channel: SMS > Email > Phone. Best time: Tue/Thu 10-12 AEST"
- Enhance with Circadian Slot (Gemini): "Based on email timestamps, she does Deep Work 2-4 PM. Don't disturb. Best window: 4:15 PM."
- Surface on contact record as "Channel DNA" intelligence panel
- Feed into Daily Command Center recommendations

**Patent candidate:** "Channel DNA Predictor — Behavioural Communication Optimisation" — 90% confidence. FILE IMMEDIATELY (Tier 1 patent).

**Technical notes:**
- New table: `channel_interactions` (channel, timestamp, response_time_seconds, responded_bool)
- Background job: recalculate Channel DNA weekly from `channel_interactions`
- New fields on `contacts`: `preferred_channel`, `preferred_times_json`, `channel_dna_data`
- Heuristic v1, not ML. Statistical analysis of response patterns.

### 2.4 Commute Briefing v1

**What it does:** Before a meeting, generates an audio briefing dynamically sized to match your travel time.

**How it works:**
- Calendar event detected → check if location requires travel
- Estimate travel duration (Google Maps API or manual input)
- Generate briefing content: contact/account summary, last interactions, deal status, recent news, competitor activity, suggested talking points
- Convert to audio via ElevenLabs (ELAINE's voice)
- Deliver as notification: "You have a 22-minute train ride. Here's a 20-minute briefing."

**Patent candidate:** "Context-Aware Commute Learning Injection" — 90% confidence. FILE IMMEDIATELY (Tier 1 patent).

**Technical notes:**
- Google Maps Distance Matrix API for travel time estimation
- Content generated via Ollama (gemma2:27b)
- Audio via ElevenLabs API (ELAINE voice_id: XQanfahzbl1YiUlZi5NW)
- Delivery: push notification + audio player in mobile PWA
- Briefing length adapts: 5-min drive = key points only. 45-min train = deep dive.

### 2.5 Rep Bias Brain

**What it does:** Profiles each sales rep's forecast bias. If you consistently say 80% and reality is 50%, Ripple corrects your probabilities.

**How it works:**
- For each rep, track: stated probability at each stage vs actual outcome
- Build bias profile: "This rep overestimates by 18% on average. Higher overestimate on large deals."
- Apply correction factor to Three Brains composite score
- Display: "Rep says 80%. History-adjusted: 62%."

**Source:** DeepSeek + Grok. Part of Patent Family 1 (Multi-Brain Decision Stack).

**Technical notes:**
- New table: `rep_forecast_history` (rep_id, deal_id, stage, stated_probability, actual_outcome, date)
- Requires minimum 20 closed deals per rep before bias becomes meaningful
- Background job: recalculate bias profiles monthly
- Feeds into Three Brains as a correction layer

### 2.6 Attention Allocation Engine

**What it does:** Shows where your attention is misallocated by comparing time spent vs revenue potential vs probability.

**How it works:**
- Track time spent per contact/account/deal (from activities)
- Compare to deal value × probability
- Flag mismatches: "You're spending 40% of your time on 12% of your revenue potential."
- Add to Daily Command Center as an insight card

**Source:** Grok.

**Technical notes:**
- Calculated from existing `activities` table (sum duration_minutes by entity)
- Cross-reference with `deals` table (amount × probability)
- New dashboard widget, not a new table

### 2.7 Social Capital Ledger

**What it does:** Tracks the informal favour economy. Introductions made, favours owed, trust deposited and withdrawn.

**How it works:**
- Track relationship "transactions": introductions made (+points), referrals given (+points), favours asked (-points), promises kept (+points), promises broken (-points)
- Running balance per contact: "You introduced Sarah to a candidate (+50). She bought lunch (-5). Net: she owes you a favour."
- "Cash In" button → drafts a referral request or introduction ask, calibrated to balance

**Source:** Gemini + Grok. Novel and patentable.

**Technical notes:**
- New table: `social_capital_transactions` (contact_id, type, points, description, date)
- Running balance calculated per contact
- Points are configurable (default: introduction = 50, referral = 30, lunch = -5, etc.)
- Integrates with Commitment Tracker (fulfilled commitment = trust deposit)

### 2.8 Mobile PWA v1

**What it does:** Responsive web app installable on mobile. Not native — PWA.

**Features:**
- Installable on iOS and Android
- Dark mode native
- Biometric authentication
- Voice CRM: "Log meeting with Sarah at Bunnings. Discussed delivery timelines. Next step: send quote by Friday." → structured record
- Business card scanner: OCR → auto-create contact with enrichment
- Nearby contacts: map view of contacts near current GPS location
- Quick log: meeting, call, note — all loggable in <30 seconds
- Today view: meetings, tasks, deals — one mobile-optimised screen
- Offline mode: full read/write access offline, conflict resolution on sync

**Technical notes:**
- Service worker for offline support
- PWA manifest for installability
- Camera access for card scanning (Tesseract.js OCR or cloud OCR)
- GPS for nearby contacts (PostGIS extension in PostgreSQL or simple Haversine formula)
- Responsive design from Phase 1 gets enhanced with mobile-specific layouts

### 2.9 Frustration Logging & Feedback Loop Infrastructure

**What it does:** Tracks every AI recommendation outcome. Did the user accept it? Did it work? This is the foundation for making Three Brains adaptive.

**How it works:**
- Every AI recommendation logged: what was suggested, was it shown, was it accepted/dismissed, what happened after
- A/B testing framework: variant A vs variant B for scoring algorithms
- Model versioning: track which version of health score / Three Brains / Channel DNA produced which outcomes
- Feeds into Phase 3 ML upgrade of Three Brains

**Source:** Manus + DeepSeek (Reinforcement Learning Loop — critical infrastructure).

**Technical notes:**
- New table: `ai_recommendations` (id, type, entity_id, recommendation, model_version, shown_at, accepted, outcome, outcome_date)
- New table: `model_versions` (id, model_name, version, config_json, deployed_at, retired_at)
- This is infrastructure, not a feature. Users don't see it. But without it, intelligence never improves.

### Phase 2 — New AI Intelligences Summary

| Brain | Build in Phase 2 | Patent Family |
|-------|-------------------|---------------|
| Rep Bias Brain | ✅ | Family 1: Multi-Brain Decision Stack |
| Attention Allocation Engine | ✅ | — (Feature, not patent) |
| Social Capital Ledger | ✅ | Family 2: Relationship Graph |
| Meeting Causality Brain | ⚠️ Start tracking, calculate after data | Family 3: Meeting & Commitment |

### Phase 2 — New UI Elements

| Element | Description |
|---------|-------------|
| Generative UI Moods | Deal in crisis → War Room (dark red, big fonts). Nurturing → softer colours, whitespace. |
| Ghost Competitor | Competitor logo fades in/out based on threat level on deal cards |
| Org Chart Heatmap | Account org chart coloured by influence, not title |
| Channel DNA Panel | On contact detail: preferred channel, best times, response pattern chart |

### Phase 2 — Patents to File

| Patent | Confidence | Action |
|--------|-----------|--------|
| Channel DNA Predictor | 90% | FILE IMMEDIATELY (provisional) |
| Commute Learning Injection | 90% | FILE IMMEDIATELY (provisional) |
| Unrecorded Meeting Intelligence | 85% | FILE IMMEDIATELY (provisional) |
| Three Brains with Rep Bias Correction | 70% | FILE after implementation |

---

# PHASE 3: SALES FORCE AUTOMATION
## Timeline: 6-12 Months After Phase 1

**Goal:** Transform Ripple from a relationship tracker into a full sales execution platform. Pipeline management, sequences, quoting, territory, forecasting.

### 3.1 Lead Management

**Lead Capture Sources:**
- Web forms: embeddable, progressive profiling (ask different questions each visit)
- Landing pages: built-in builder or Spark marketing integration
- Chatbot: ELAINE-powered conversational capture
- Email: forward-to-CRM address, auto-create lead from inbound
- Business card scanner (from Phase 2 mobile)
- LinkedIn: browser extension captures profiles into Ripple
- Snitcher: anonymous web visitors → auto-create company lead
- Referrals: source attribution + referrer commission tracking
- Events: QR code check-in → auto-create lead. Badge scan import.
- API: webhook + REST for any external source

**Lead Scoring — Three-Axis Model:**
- **Fit (Logic Brain):** ICP matching — firmographics, technographics, budget signals. Rule-based + ML.
- **Intent (Evidence Brain):** Behavioural signals — web visits, content downloads, email engagement, event attendance. Engagement scoring with decay.
- **Instinct (Instinct Brain):** AI-inferred — sentiment, social activity, competitive mentions, timing. LLM analysis via Ollama.
- Combined with explainable output: "Scored 78 because: ICP match 92%, pricing page 3x (+15), 14 days inactive (-12), competitor engagement (-7)."

**Lead Routing:**
- Territory-based (AU state/postcode)
- Round-robin (equal distribution)
- Weighted (by rep capacity, pipeline, win rate)
- AI-optimised (ELAINE routes to rep with highest predicted close probability)
- Carbon-aware (routes to nearest rep when in-person likely)

**Lead Conversion:**
- One-click: Lead → Contact + Account + Deal
- Smart field mapping, auto-populate
- Merge with existing contact/account if duplicate detected
- Conversion audit trail

**Technical notes:**
- New tables: `leads` (similar to contacts but pre-conversion), `lead_scores`, `lead_routing_rules`
- Lead conversion creates entries in existing `contacts`, `accounts`, `deals` tables
- Scoring models in `model_versions` table (from Phase 2 feedback loop)

### 3.2 Sales Sequences & Cadences

**Multi-Channel Sequences:**
- Email: templates, personalisation tokens, A/B testing, send-time optimisation
- SMS: via TextBee.dev. Personalised. Compliance-aware (opt-in tracking).
- Phone: call task with suggested script and talking points from Three Brains
- LinkedIn: connection request, InMail, post engagement — task-based (manual, tracked)
- Voice note: ElevenLabs-generated personalised audio via ELAINE
- Direct mail: task to send handwritten note or gift, tracked

**Sequence Intelligence:**
- A/B testing: subject lines, send times, channel order
- Optimal sequence: AI recommends order based on contact's Channel DNA
- Fatigue detection: "Sarah has received 5 touches in 10 days. She's disengaging. Pause 7 days."
- Reply detection: auto-pause sequence, route to human
- Sentiment analysis: "Sarah's reply is negative. Flag for human review."
- Performance analytics: open rates, reply rates, meeting booked rates per sequence/step/rep

**Technical notes:**
- New tables: `sequences`, `sequence_steps`, `sequence_enrolments`, `sequence_events`
- TextBee.dev integration for SMS
- ElevenLabs integration for voice notes (reuse ELAINE voice)
- Sequence engine runs as background job (APScheduler or dedicated worker)

### 3.3 Quoting & CPQ (Configure-Price-Quote)

**Product Catalog:**
- Products: name, SKU, description, category, images
- Pricing: list price, cost price, margin, currency (AUD default)
- Price books: multiple per region, customer tier, volume
- Bundles: pre-configured with discounted pricing
- Subscriptions: monthly/annual/custom billing periods
- Usage-based: metered pricing with tier thresholds

**Quote Builder:**
- Drag-and-drop product selection
- Real-time margin calculator
- Discount approval: configurable thresholds (>10% needs manager, >20% needs director)
- Branded templates (AMTL design system)
- E-signature: built-in or DocuSign/Adobe Sign integration
- Quote tracking: "Sarah viewed quote for 4 min. Spent 2 min on pricing page."
- Versioning: full history, side-by-side comparison
- PDF or shareable web link with analytics

**Proposal Generator:**
- AI-generated proposals from deal context + product selection + company research
- Content library: reusable sections (About Us, Case Studies, Methodology, Terms)
- Auto-personalisation: contact name, company, industry examples, relevant case studies
- Competitor positioning: auto-insert battle card content if competitor on deal
- Approval workflow before sending
- Send and track: opens, page views, forwards

**Ripple Innovation — "Smart Pricing":**
AI suggests optimal price point based on deal similarity analysis, competitor intelligence, and customer payment history (from Genie). "Deals like this close 28% faster at $X price point."

**Technical notes:**
- New tables: `products`, `price_books`, `price_book_entries`, `quotes`, `quote_line_items`, `quote_versions`, `proposals`
- Genie integration for payment history data
- PDF generation (from Phase 1 DSAR experience, extend to quote/proposal PDFs)
- E-signature: start with simple "accept" link, integrate DocuSign later

### 3.4 Territory Management

**Territory Structure:**
- Region (ANZ, APAC, Global)
- State/Territory (NSW, VIC, QLD, WA, SA, TAS, NT, ACT, NZ-NI, NZ-SI)
- Postcode band (2000-2099 Sydney CBD, 3000-3099 Melbourne CBD)
- Industry vertical (Technology, Healthcare, Manufacturing, Professional Services)
- Named accounts (specific companies → specific reps)

**Territory Intelligence:**
- Interactive territory map (all accounts, deals, travel routes)
- Performance comparison: side-by-side territory metrics (pipeline, revenue, win rate, deal size)
- Capacity planning: "Rep A has 42 deals (capacity: 35). Rep B has 18. Rebalance recommended."
- Carbon-optimised routing: "Move these 3 accounts from Rep A (Wollongong) to Rep B (Parramatta) — carbon drops 23%."
- Territory handoff: automated workflow with warm intro templates, deal transfer, relationship history

**Technical notes:**
- New tables: `territories`, `territory_assignments`, `territory_history`
- Map integration: Google Maps or Mapbox
- Carbon calculation: distance × emissions factor per transport mode

### 3.5 Sales Forecasting with Three Brains

**Forecasting Features:**
- Weighted pipeline: deal value × probability at each stage
- AI forecast: Three Brains probability vs rep-stated probability. "AI predicts $420K. Reps predict $580K. Historical accuracy: AI is closer 73% of the time."
- Scenario planning: best case / commit / worst case with deal-level toggles
- Forecast categories: Pipeline, Best Case, Commit, Closed (configurable per stage)
- Forecast hierarchy: Rep → Manager → Director. Roll-up with override tracking.
- Accuracy tracking: "Your forecast accuracy last quarter: ±14%. Industry benchmark: ±18%."

**Revenue Intelligence (Clari-Style):**
- Pipeline inspection: deal-by-deal with AI risk flags
- Deal velocity: days in each stage vs benchmark
- Engagement score per deal: "Decision maker hasn't engaged in 21 days."
- Coverage ratio: "Need 3x pipeline to hit target. Currently 2.4x. Gap: $180K needed."
- Win rate analysis: by rep, territory, product, deal size, industry
- Revenue leakage: "12 deals worth $340K lost to 'no decision'. 8 stalled in Proposal."

**Technical notes:**
- Builds on Three Brains from Phase 1 + Rep Bias correction from Phase 2
- New tables: `forecasts`, `forecast_entries`, `forecast_snapshots`
- Snapshot: weekly capture of pipeline state for trend analysis
- Phase 3 is when Three Brains upgrades from heuristic to ML (using Phase 2 feedback loop data)

### 3.6 Carbon-Aware Deal Economics

**What it does:** Carbon isn't a calculator — it's a financial variable in deal economics.

**Features:**
- Carbon cost integrated into deal profitability: "If you discount 10%, carbon cost of travel means net profit is actually negative. Max discount: 7%."
- Carbon-aware territory routing (see 3.4)
- Travel intelligence panel on contacts: distance, cost, carbon, visit history
- Decision support: "In-person still worth it" vs "Switch to remote. Trust is stable."
- Carbon P&L: total emissions per deal, per rep, per territory

**Source:** Original spec + Thalaiva upgrade (carbon as financial liability, not just tracker).

**Patent candidate:** "Carbon-Aware Deal Economics & Territory Routing" — 85% confidence. Part of Patent Family 2.

**Technical notes:**
- New table: `travel_logs` (contact_id, deal_id, distance_km, transport_mode, carbon_kg, cost_aud)
- Carbon factors: configurable per transport mode (car, train, plane, bike)
- Integrates into quote margin calculation
- New fields on deals: `total_travel_carbon`, `carbon_adjusted_margin`

### Phase 3 — New AI Intelligences

| Brain | Build in Phase 3 | Patent Family |
|-------|-------------------|---------------|
| Relationship Cost & Carbon Brain | ✅ | Family 2: Relationship Graph & Carbon |
| Echo-Ripple Brain | ✅ (requires Echo data) | — |
| Causal Inference Engine | ⚠️ Start, needs historical data | — |
| Meeting Causality Brain | ✅ (now has enough data) | Family 3: Meeting & Commitment |

### Phase 3 — Three Brains ML Upgrade

With Phase 2's feedback loop data (6+ months of recommendation tracking), upgrade Three Brains from heuristic to ML:
- Train on historical deals: features → outcome
- A/B test: heuristic vs ML scoring
- Adversarial mode (Thalaiva): "You say 80%. I disagree. Here are 3 similar deals you rated 80% that closed at 45%."
- Model versioning and continuous retraining

---

# PHASE 4: ADVANCED & AGENTIC
## Timeline: 12-24 Months After Phase 1

**Goal:** Transform Ripple from a tool you use into a teammate that acts. Graduated autonomy. Digital twins. Agent fleet. Graph database. This is the 2036 vision.

### 4.1 Contract Lifecycle Management

**Contract Stages:** Draft → Review → Negotiate → Approve → Sign → Active → Renew/Amend → Expire/Terminate

**Features:**
- Template-based generation, auto-populated from deal record
- Clause library with compliance ratings ("This clause is ISO 27001 compliant")
- Internal review workflow with track changes and version comparison
- External collaboration: customer can comment/suggest via secure portal
- Multi-level approval: configurable rules (value thresholds, non-standard terms)
- E-signature (built-in or DocuSign/Adobe Sign)
- Key date tracking: renewal reminders at 90/60/30 days
- Amendment workflow
- Auto-generate renewal quote

**Contract Intelligence:**
- Risk scoring: AI analyses terms for non-standard clauses, unfavourable payment terms, excessive liability
- Obligation tracking: extract obligations from text, track fulfilment, alert on deadlines
- Auto-renewal detection: "Auto-renews in 45 days. Customer satisfaction: 72% (amber). Review."
- Revenue recognition: link terms to revenue schedule, feed to Genie for ASC 116/IFRS 15
- Full-text search across all contracts

**Ripple Innovation — "Contract Health Score":**
Composite of: days to sign (vs benchmark), negotiation rounds, clause deviation, payment term deviation. "Healthy contracts close in 14 days. This one at 32 — investigate."

**Technical notes:**
- New tables: `contracts`, `contract_versions`, `contract_clauses`, `clause_library`, `contract_obligations`, `contract_approvals`
- Document storage: contract files stored locally (Dropbox path)
- Integration with quote system (Phase 3) for auto-generation

### 4.2 Commission & Incentive Management

**Features:**
- Plan builder: base + commission %, tiered accelerators above quota, split deals
- Multi-currency: AUD, NZD, USD with exchange rate management
- Quota management: set, track, adjust per rep/territory/product
- Auto-calculate on deal close, preview before finalisation
- Genie integration for payroll processing
- Dispute resolution workflow
- What-if calculator: "If I close this deal, my commission = $X this quarter"

**Technical notes:**
- New tables: `commission_plans`, `commission_rules`, `quotas`, `commission_calculations`, `commission_disputes`
- Genie integration: feed calculated commissions for payroll
- Closed Won celebration (Phase 1 UI element) now shows real commission counter

### 4.3 Digital Twin Sandbox

**The Innovation:** For every active contact, create a "synthetic version" trained on all historical interactions. Use for practice and war-gaming.

**Features (Prototype):**
- Simulate call: AI plays "Synthetic Sarah" based on her emails, LinkedIn posts, Channel DNA, personality profile
- Practice pitches, score performance: "You triggered her price sensitivity. Lead with value instead."
- War gaming: run 1,000 negotiation scenarios to find optimal strategy before real meeting
- Agent certification: AI agents must pass exams in sandbox before being allowed to send real communications

**Source:** Gemini ("Holodeck") + Manus ("Digital Twin Sandbox").

**Patent candidate:** "System for Creating Dynamic, Learning Digital Twins for Sales Agent Training & Certification" — 95% confidence. Highest-confidence patent in entire portfolio.

**Technical notes:**
- Fine-tune small LLM per contact using historical interaction data
- Requires significant GPU: likely need to upgrade from RTX 5070 or use cloud for training
- Evaluation framework: score practice sessions on rapport, objection handling, value communication
- Sandbox environment isolated from production data

### 4.4 ELAINE Graduated Autonomy

**The Paradigm Shift:**
```
TODAY:  Event → CRM records → AI suggests → Human does
2036:  AI senses → AI thinks → AI acts within guardrails → AI learns → Human only for exceptions
```

**Autonomy Levels (Configurable per action type):**
- **Level 0 — Suggest Only:** ELAINE recommends, human decides and executes
- **Level 1 — Draft for Approval:** ELAINE drafts email/action, human reviews and sends
- **Level 2 — Auto-Execute Low Risk:** ELAINE sends follow-up emails, logs activities, updates fields — automatically. Human notified.
- **Level 3 — Full Autonomy:** ELAINE handles entire sequences within guardrails. Human only for exceptions.

**Guardrail Framework:**
- Maximum deal value for auto-actions (e.g., Level 2 only for deals < $10K)
- Maximum email send rate per day
- Escalation triggers: negative sentiment detected, customer complaint, deal value above threshold
- Human override always available
- Full audit trail of every autonomous action

**Patent candidate:** "Graduated Autonomous Execution Engine with Role-Based Authority Thresholds" — 85% confidence. Part of Patent Family 5.

**Technical notes:**
- New table: `autonomy_config` (action_type, autonomy_level, guardrails_json)
- New table: `autonomous_actions_log` (action, level, trigger, outcome, human_override_used)
- ELAINE v5 architecture: Agent → Guardrail Check → Execute or Escalate

### 4.5 Agent Fleet

**Specialised Agents (First 2-3):**

| Agent | What It Does | Autonomy Level |
|-------|-------------|----------------|
| **ProspectorAgent** | Monitors Snitcher + social signals, identifies new prospects, enriches, adds to pipeline | Level 1-2 |
| **OutreachAgent** | Executes sales sequences, personalises messages, handles follow-ups | Level 1-2 |
| **MeetingAgent** | Schedules meetings, generates prep briefs, captures notes, extracts commitments | Level 2 |

**How agents work:**
- Each agent has a specific scope, set of tools, and autonomy level
- Agents run on defined schedules (every 4 hours) or triggered by events
- All actions logged with full audit trail
- Agents must pass Digital Twin Sandbox certification before handling real contacts

**Source:** Thalaiva + Manus.

**Technical notes:**
- Agent architecture: Sense → Think → Act → Learn loop (DeepSeek's OS loop)
- Each agent is a Python class with: `sense()`, `think()`, `act()`, `learn()` methods
- Orchestrated by ELAINE (she's the agent manager)
- Uses Supervisor for GPU scheduling (agents may need LLM reasoning)

### 4.6 Revenue Intelligence

**Advanced Analytics:**
- Revenue waterfall: new + expansion + renewal - churn - contraction
- Cohort analysis: revenue retention by customer vintage
- Customer lifetime value (CLV) prediction
- Net Revenue Retention (NRR) tracking
- Revenue attribution: which activities, channels, and sequences drive revenue

**Technical notes:**
- Builds on Phase 3 forecasting data
- Genie integration for actual revenue data (invoices, payments)
- New dashboard: Revenue Intelligence (executive view)

### 4.7 Graph Database Migration

**The Architectural Leap:**

Current: PostgreSQL relational tables with foreign keys  
Target: PostgreSQL + Apache AGE (graph extension) OR Neo4j alongside PostgreSQL

**Why graph matters:**
- Every relationship is a first-class mathematical object, not a join table
- Query: "Who can introduce me to the CTO of TechCo?" → traverse influence paths
- Query: "What's the shortest trust path from me to Sarah's decision maker?"
- Network centrality: identify most connected, most influential nodes
- Warm intro path finding: relationship chains across your entire network
- Relationship inheritance: "Sarah moved to NewCo. Bring her relationship history."

**Graph nodes:** People, Companies, Deals, Commitments, Communications, Events, Products, Meetings  
**Graph edges:** Influences, Reports_to, Promised, Paid, Introduced_by, Mentioned_competitor, Attended_meeting_with, Complained_about, Championed_deal, Works_with

**Source:** Grok + DeepSeek. "This is how you become 10 years ahead."

**Technical notes:**
- Apache AGE: PostgreSQL extension, keeps everything in one database
- Alternative: Neo4j as separate service (new Docker container, new port)
- Migration: create graph views on top of existing relational data first, then gradually move queries
- pgvector (embeddings) + AGE (graph) + PostgreSQL (relational) = powerful hybrid

### 4.8 Game Theory Engine

**What it does:** Applies game theory to negotiations. "Hold firm — 90% chance they fold based on similar historical scenarios."

**Source:** Gemini. Requires significant historical data and research.

**Technical notes:**
- Nash equilibrium calculations for negotiation scenarios
- Requires 500+ closed deals for meaningful patterns
- May integrate with Digital Twin Sandbox for simulation

### Phase 4 — New AI Intelligences

| Brain | Build in Phase 4 | Patent Family |
|-------|-------------------|---------------|
| Game Theory Engine | ✅ | — (Research needed) |
| Causal Inference Engine | ✅ (now has enough data) | — |
| Adversarial Three Brains (full ML) | ✅ | Family 1: Multi-Brain Decision Stack |

### Phase 4 — UI Innovations

| Element | Description |
|---------|-------------|
| Physics Engine Deal Cards | Heavy ball rolling up hill. Momentum drops → ball rolls backward. |
| God Mode Galaxy View | 3D network visualisation. Trust links as glowing beams. Fly through like Iron Man. |
| AI-to-AI Negotiation View | Watch your agent negotiate with customer's procurement AI. Human override always available. |

---

# CROSS-PHASE: REPORTING & DASHBOARDS
## Build incrementally across all phases

### Pre-Built Reports (add as data becomes available)

| Category | Phase Available | Reports |
|----------|----------------|---------|
| **Pipeline** | Phase 1 | By stage, weighted value, velocity |
| **Activity** | Phase 1 | Per contact, per deal, per day |
| **Commitment** | Phase 1 | Fulfilment rates, overdue, by contact |
| **Privacy** | Phase 1 | DSAR volume, consent coverage |
| **Revenue** | Phase 3 | Closed won, forecast vs actual, trends |
| **Lead** | Phase 3 | Sources, conversion rates, scoring accuracy |
| **Territory** | Phase 3 | Performance comparison, carbon, capacity |
| **Commission** | Phase 4 | Earned, pending, paid by rep |
| **Travel** | Phase 3 | Total km, cost, carbon by rep/territory |
| **Meeting** | Phase 2 | Frequency, duration, actions, meeting-to-close |

### Custom Report Builder (Phase 3)
- Drag-and-drop field selection
- Filter, group, pivot, sort
- Visualisation: bar, line, pie, funnel, scatter, heatmap, gauge, table
- Schedule: daily/weekly/monthly email delivery
- Export: PDF, Excel, CSV
- Share: link, embed, dashboard

### Dashboard Design Principle
Every dashboard should look like a Bloomberg terminal — dense with information but visually elegant. No wasted space. No ugly default charts. AMTL Midnight dark mode.

---

# CROSS-PHASE: WORKFLOW & AUTOMATION ENGINE
## Phase 2 foundation, Phase 3 full build

### Trigger → Condition → Action Framework

| Triggers | Conditions | Actions |
|----------|-----------|---------|
| Deal stage change | Value > $X | Send email |
| Lead created | Source = web | Assign to rep |
| Email opened | Contact = Decision Maker | Create task |
| Meeting completed | Sentiment = negative | Alert manager |
| Quote viewed | Time on pricing > 2 min | Notify rep |
| Contract expiring | Days until expiry < 90 | Start renewal sequence |
| Relationship health drops | Score < 40 | Escalate to manager |
| Payment overdue (Genie) | Days > 30 | Flag on deal |

### ELAINE Orchestration (Phase 4)
Multi-step agentic workflows with approval gates. Not just "if X then Y."

Example: "When deal moves to Negotiation → Generate contract draft → Route to legal → If approved, send to customer → Track views → If not signed in 7 days, reminder → If not signed in 14 days, alert rep → If signed, create invoice in Genie."

---

# CROSS-PHASE: MARKETING CONNECTION (SPARK)
## Phase 3-4

### Spark Integration (Three Marketing Brains)

| Integration | Description |
|-------------|-------------|
| Lead flow | Marketing qualified leads flow from Spark → Ripple automatically |
| Campaign attribution | Multi-touch attribution on contact and deal records |
| Content engagement | Downloads, webinar attendance, ad clicks → logged to timeline |
| Audience sync | Ripple segments available as Spark audiences |
| ROI reporting | Campaign → Lead → Deal → Revenue. Full funnel. |
| ABM coordination | Target account lists shared. Coordinated outreach. |

---

# PATENT PORTFOLIO — FULL FILING SCHEDULE

## Phase 1 (File Provisionals Immediately)

| # | Patent | Family | Confidence |
|---|--------|--------|-----------|
| 1 | Automated DSAR Fulfilment with Self-Service Privacy Portal | Family 4: Privacy & Transparency | 95% |
| 2 | AI-Powered Bilateral Commitment Tracking with Revenue Impact | Family 3: Meeting & Commitment | 75% |
| 3 | Graduated Autonomous Execution Engine (provisional) | Family 5: Agentic Architecture | 85% |

## Phase 2 (File Provisionals)

| # | Patent | Family | Confidence |
|---|--------|--------|-----------|
| 4 | Channel DNA Predictor — Behavioural Communication Optimisation | Family 2: Relationship Graph | 90% |
| 5 | Context-Aware Commute Learning Injection | Mobile | 90% |
| 6 | Unrecorded Meeting Intelligence with Immediate Audio Deletion | Family 3: Meeting & Commitment | 85% |

## Phase 3 (Convert to Full Utility)

| # | Patent | Family | Confidence |
|---|--------|--------|-----------|
| 7 | Carbon-Aware Deal Economics & Territory Routing | Family 2: Relationship Graph & Carbon | 85% |
| 8 | Three Brains Adversarial Decision Engine with Outcome Feedback | Family 1: Multi-Brain Decision Stack | 70% |

## Phase 4 (File After Implementation)

| # | Patent | Family | Confidence |
|---|--------|--------|-----------|
| 9 | Digital Twin Sandbox for Sales Agent Training & Certification | Simulation | 95% |
| 10 | Ripple Protocol — Inter-Agent Commerce Communication Standard | Network Protocol | 90% |
| 11 | Meeting Causality Engine | Family 3: Meeting & Commitment | 60% |
| 12 | Ambient Activity Capture from Passive Audio + Location + Calendar | Mobile/AI | 80% |

### Patent Family Strategy (5 Families)

| Family | Contents | Core Innovation |
|--------|----------|----------------|
| **1. Multi-Brain Decision Stack** | Three Brains + Adversarial + Rep Bias + Outcome Feedback | Per-rep calibration, explainability, weight adaptation |
| **2. Relationship Graph & Carbon** | Relationship Memory Graph + Trust Decay + Carbon Territory | Joint optimisation of relationship + revenue + cost + emissions |
| **3. Meeting & Commitment Causality** | Meeting Causality + Commitment Brain + Unrecorded Meeting | Extracting commitments, tracking fulfilment, causality |
| **4. Privacy & Transparency Portal** | Automated DSAR + Self-Service + Proactive Notification | Identity verification, audit trail, consent management |
| **5. Agentic Execution Architecture** | ELAINE Orchestration + Graduated Autonomy + Agent Fleet | Configurable authority thresholds, Digital Twin certification |

**Estimated budget:** $300K-$525K over 3 years for full portfolio (Manus estimate).

---

# THE 2036 QUESTIONS
## For Future LLM Consultations

These are the hard questions raised by reviewers that should inform Phases 3-4 architecture:

1. "In 2036, what percentage of B2B sales conversations will involve a human on both sides?"
2. "Design a CRM that requires zero data entry. All data inferred from passive signals. What's the architecture?"
3. "What would it take for AI to negotiate a contract independently?"
4. "How do you quantify the financial value of a business relationship? What signals? What validation?"
5. "Meetings are the default coordination mechanism. What would a world look like where meetings are the exception?"
6. "What graph database architecture best supports a Relationship Operating System?"
7. "How do you build user trust in AI recommendations? What's minimum viable proof?"
8. "What's the optimal cognitive load for a CRM — how many AI insights per screen before users tune out?"

---

# GUIDING PRINCIPLES — APPLY TO ALL PHASES

### From the Reviewers

> *"Stop being tool. Start being teammate."* — Gemini

> *"Market doesn't reward impressive specs. It rewards daily behaviour change."* — Grok

> *"Do not waste this opportunity building better horse."* — Thalaiva

> *"Every screen has AI. Every field has AI. Dangerous. If everything is intelligent: nothing is intelligent."* — Grok

> *"AI only when it meaningfully changes a decision."* — Grok

### Intelligence Tier Model (Apply to All Features)

| Tier | Method | Cost | When |
|------|--------|------|------|
| Tier 1 | Lightweight heuristics | Fast, free | Default for everything |
| Tier 2 | Cached ML predictions | Medium | Scheduled recalculation |
| Tier 3 | On-demand LLM reasoning | Expensive, slow | Only when it meaningfully changes a decision |

### UX Simplification Rule (DeepSeek)

For every object (Contact, Account, Deal):
- **Top:** Today's judgment (one sentence)
- **Middle:** Core fields + 1-2 intelligence panels
- **Bottom:** Timeline

Advanced brains surface as insight snippets, NOT new panels. Cognitive load must decrease, not increase, with each phase.

---

*"Ship Phase 1. File patents. Build future in parallel — but only in parallel, never instead."*

# RIPPLE v3 — COMPLETE CRM FEATURE SPECIFICATION
## Contact Management + Sales Force Automation + Intelligence Layers
**Date:** 12 February 2026  
**Author:** Thalaiva (Strategic Advisor) for Almost Magic Tech Lab  
**Status:** Living document — synthesised from all LLM feedback + competitive research

---

## PHILOSOPHY

Ripple is not a CRM. It is an **Agentic Relationship Operating System (ROS)**.

Three design principles:
1. **Zero typing wherever possible** — voice, auto-capture, AI inference
2. **Intelligence, not just information** — every screen tells you what to do next
3. **Sexy by default** — if it doesn't look better than Salesforce Lightning, it doesn't ship

UI design rule: Salesforce wins because of its UI. Dynamics fails because of its UI. Ripple must be the CRM people *want* to open. Dark mode native (AMTL Midnight #0A0E14 + Gold #D4AF37), micro-animations on every interaction, zero visual clutter, progressive disclosure. Every screen should feel like a Bloomberg terminal crossed with a luxury watch app.

---

# PART A: CONTACT MANAGEMENT

## 1. Contact Records

### 1.1 Core Fields
| Field | Standard | Ripple Intelligence Layer |
|---|---|---|
| Name | First, Last, Prefix, Suffix | Auto-detect cultural naming conventions (Asian family-name-first, etc.) |
| Email | Primary, Secondary, Personal | Auto-detect primary from response frequency |
| Phone | Work, Mobile, Direct | **Channel DNA**: "Responds to SMS in 4 min, email in 2.1 hrs, phone in 4 hrs" |
| Address | Street, City, State, Post, Country | **Travel Intelligence Panel** (distance, cost, carbon, history) |
| Title/Role | Job Title, Department, Seniority | **Title Change Detection** from email signatures — auto-update + alert |
| Company | Associated Account | **Cross-Company Graph**: all organisations this person connects to |
| Timezone | Auto-derived from address | **Contact-Level Clock**: "It's 3:47 PM for Sarah right now. Good time to call." |
| Social | LinkedIn, Twitter/X, Facebook | **Social Activity Monitor**: "Sarah posted about AI governance on LinkedIn 2 hours ago" |
| Source | Lead source, campaign | Multi-touch attribution — first touch + last touch + weighted |
| Owner | Assigned rep | Territory-aware with carbon-optimised routing |

### 1.2 Intelligence Fields (Nobody Else Has These)

| Field | What It Does | Patent Potential |
|---|---|---|
| **Channel DNA** | Auto-detected communication preferences from response latency, open rates, click patterns. "Best channel: SMS > Email > Phone. Best time: Tue/Thu 10-12 AEST" | ✅ File now |
| **Relationship Health Score** | Composite score (0-100) from response latency + meeting frequency + sentiment trend + commitment fulfilment + social interaction. Red/Amber/Green. | ✅ Novel |
| **Trust Decay Indicator** | Days since last meaningful interaction vs baseline frequency. "Sarah's trust is decaying — 45 days since contact (baseline: 12 days)" | ✅ Novel |
| **Influence Score** | "When Sarah is involved, deals close 23% faster." Quantifies relationship value in dollars. | ✅ Novel |
| **Tenure & Anniversary** | "3-year customer" badges. Anniversary alerts. Tenure-based pricing recommendations. | Feature (not patentable) |
| **Cognitive Profile** | Communication style analysis: analytical, driver, expressive, amiable. Adapts ELAINE's suggested approach. | ⚠️ Possible |
| **Sentiment Trend** | Tracks sentiment across last 10 interactions. Rising/stable/declining with sparkline. | Feature |
| **Next Best Action** | Three Brains recommendation: "Call Sarah today. Trust decaying. Deal at risk. Carbon cost: $12." | ✅ Part of Three Brains patent |

### 1.3 Activity Timeline
Every interaction on a single, searchable, filterable timeline:
- Emails (sent, received, opened, clicked, replied)
- Calls (logged, duration, outcome, recording link if permitted)
- Meetings (scheduled, attended, notes, actions, Follow Me prompts)
- Notes (manual, structured, voice-captured)
- Tasks (assigned, completed, overdue)
- Documents (sent, viewed, time spent on each page)
- Social touches (LinkedIn messages, connections, comments)
- Travel (visits logged with distance, cost, carbon)
- Deal stage changes
- Quotes/proposals sent
- Payments received (via Genie integration)
- Support tickets (if service module active)
- ELAINE actions taken on this contact

### 1.4 Data Enrichment — Four-Layer Stack
| Layer | Source | What It Provides |
|---|---|---|
| **Snitcher** | Web visitor identification | Company name, pages visited, visit frequency, intent signals |
| **Identity Atlas** | ABR (Australian Business Register) + ABN Lookup | ABN, ACN, entity type, GST status, business name, registered address, 50+ fields auto-filled |
| **Echo** | LLM visibility monitoring | How this person/company appears in AI responses. "TechCo is mentioned positively in 4/5 LLMs for cybersecurity in Australia" |
| **Social Enrichment** | LinkedIn + public profiles | Current title, employment history, education, mutual connections, recent posts |

### 1.5 Duplicate Detection & Merge
- AI-powered fuzzy matching (name, email, phone, ABN)
- Confidence scoring: "85% likely duplicate"
- One-click merge with field-by-field selection
- Merge audit trail (who merged, when, which fields kept)
- Auto-suggestion on contact creation: "This looks like an existing contact"

### 1.6 Contact Segmentation & Views
- Smart lists with dynamic filters (any field combination)
- Saved views per user
- Segment by: lifecycle stage, relationship health, deal value, territory, industry, engagement score
- Visual segment builder (drag-and-drop, no code)

---

## 2. Company/Account Management

### 2.1 Account Record
| Field | Standard | Ripple Intelligence |
|---|---|---|
| Company Name | Legal + trading names | ABN auto-fill populates 50+ fields |
| Industry | ANZSIC codes | Industry benchmarking against Genie data |
| Revenue | Annual revenue | **Revenue Intelligence**: trend from public data + Genie invoicing |
| Size | Employee count | Growth/contraction tracking over time |
| Website | URL | Snitcher integration: "12 visits this month from 3 different people" |
| Parent/Child | Account hierarchy | Multi-entity relationship tree |
| Territory | State/region | Carbon-optimised territory assignment |
| Account Health | Overall score | Composite of all contact relationship health scores + payment history + deal velocity |

### 2.2 Account Intelligence

| Feature | Description |
|---|---|
| **Org Chart Builder** | Visual hierarchy: who reports to whom, who influences whom. Drag-and-drop. Identifies gaps: "No contact in IT department — risk for tech deals." |
| **Stakeholder Map** | Per deal: Champion, Decision Maker, Influencer, Blocker, End User. Visual map with relationship lines. |
| **Company Timeline** | All activities across all contacts at this company. Unified view. |
| **Revenue Rollup** | Total lifetime value, current pipeline, average deal size, win rate at this account. |
| **Competitive Presence** | Which competitors are active at this account (from meeting notes, email analysis, social signals). |
| **Relationship Inheritance** | New contact joins company → "This person previously worked at TechCo (your customer). They know James from your team. Warm intro path available." |
| **Payment Health** (Genie) | Average days to pay, outstanding invoices, credit risk score from Genie's debtor scoring engine. |

### 2.3 Account-Based Marketing (ABM)

| Feature | Description | Competitors |
|---|---|---|
| **ICP Scoring** | Ideal Customer Profile matching. Firmographic + technographic + behavioural. Score 0-100. | Salesforce (Pardot), HubSpot (Enterprise) |
| **Target Account Lists** | Curated lists of high-value prospects. Shared across sales + marketing. | HubSpot, Terminus |
| **Account Engagement Score** | Cross-contact engagement: web visits + email opens + meeting attendance + social interaction. | 6sense, Demandbase |
| **Snitcher Web Intent** | "TechCo visited your pricing page 3 times this week from 2 different IPs." | Leadfeeder, Clearbit |
| **Account Playbooks** | Pre-built outreach sequences for target accounts. ELAINE executes. | Salesforce, Outreach |

**Ripple Innovation:** ABM + Carbon Awareness. "This target account is 8 km away. In-person approach has 3x higher conversion for ANZ SMBs. Carbon cost: 1.7 kg CO₂. Worth it."

---

## 3. Lead Management

### 3.1 Lead Capture
| Source | How It Works |
|---|---|
| **Web Forms** | Embeddable forms. Progressive profiling (ask different questions each visit). |
| **Landing Pages** | Built-in page builder (or integrate with Spark marketing). |
| **Chatbot** | ELAINE-powered conversational capture. "Hi, I see you're looking at our governance services. Want to chat?" |
| **Email** | Forward-to-CRM email address. Auto-create lead from inbound email. |
| **Business Cards** | Mobile: scan card → OCR → auto-create lead with enrichment. |
| **LinkedIn** | Browser extension captures LinkedIn profiles into Ripple. |
| **Snitcher** | Anonymous web visitors identified → auto-create company lead. |
| **Referrals** | Referral tracking with source attribution + referrer commission tracking. |
| **Events** | QR code check-in → auto-create lead. Badge scan import. |
| **API** | Webhook + REST API for any external source. |

### 3.2 Lead Scoring — Three-Axis Model

| Axis | What It Measures | Method |
|---|---|---|
| **Fit** (Logic Brain) | How well this lead matches ICP. Firmographics, technographics, budget signals. | Rule-based + ML scoring |
| **Intent** (Evidence Brain) | Behavioural signals: web visits, content downloads, email engagement, event attendance. | Engagement scoring + decay |
| **Instinct** (Instinct Brain) | AI-inferred signals: sentiment analysis, social activity, competitive mentions, timing signals. | LLM analysis via Ollama |

**Combined Score:** Weighted average with adaptive weighting based on historical win/loss analysis. "Leads with high Fit + high Intent close 4.2x faster than those with only high Fit."

**Ripple Innovation:** Explainable scoring. "This lead scored 78 because: ICP match 92%, visited pricing page 3x (Intent +15), but hasn't engaged in 14 days (decay -12), and LinkedIn shows competitor engagement (Instinct -7)."

### 3.3 Lead Routing
| Method | Description |
|---|---|
| **Territory** | AU state/postcode-based assignment |
| **Round-Robin** | Equal distribution across team |
| **Weighted** | Based on rep capacity, current pipeline, win rate |
| **AI-Optimised** | ELAINE routes to rep with highest predicted close probability for this lead type |
| **Carbon-Aware** | Routes to nearest rep when in-person is likely (reduces travel) |

### 3.4 Lead Conversion
- One-click convert: Lead → Contact + Account + Opportunity
- Smart mapping: auto-populate all fields
- Conversion audit trail
- Option to create deal immediately or just contact/account
- Merge with existing contact/account if duplicate detected

---

# PART B: SALES FORCE AUTOMATION

## 4. Opportunity/Deal Management

### 4.1 Pipeline
| Feature | Description | Ripple Intelligence |
|---|---|---|
| **Kanban Board** | Drag-and-drop deal cards across stages | Cards show: value, probability, days in stage, health indicator, next action |
| **List View** | Sortable, filterable table | Bulk actions: update stage, assign owner, add to sequence |
| **Map View** | Deals plotted on map by contact location | Travel-optimised: "These 3 deals are within 5 km. Visit all today." |
| **Forecast View** | Pipeline by expected close date | Three Brains probability vs rep-stated probability side by side |
| **Timeline View** | Gantt-style view of deal progression | Highlights stalled deals and velocity outliers |

### 4.2 Deal Record
| Section | Fields | Intelligence |
|---|---|---|
| **Header** | Deal name, value, stage, probability, close date, owner | Health indicator (green/amber/red) + AI confidence |
| **Contacts** | All associated contacts with roles | Stakeholder map: Champion, Decision Maker, Blocker identified |
| **Products** | Line items from product catalog | Margin calculator, discount approval workflow |
| **Activity** | Timeline of all interactions | "12 activities in 30 days. Average winning deal: 18. Needs more engagement." |
| **Competitors** | Active competitors on this deal | Battle cards auto-surfaced. "Competitor X was mentioned in last meeting." |
| **Documents** | Quotes, proposals, contracts | View tracking: "Sarah spent 4 min on pricing page, 30 sec on terms." |
| **Notes** | Structured meeting notes + actions | AI-extracted commitments: "Sarah promised budget approval by Friday." |
| **Financials** | Revenue schedule, payment terms | Genie integration: invoice generation from won deal |

### 4.3 Deal Intelligence (Ripple Exclusive)

| Feature | Description | Patent? |
|---|---|---|
| **Win/Loss Autopsy** | Post-close analysis. "You won because: price competitive (+15), relationship strong (+22), technical fit (+18). You almost lost because: slow response time (-8)." | ⚠️ Possible |
| **Stall Detection** | "This deal has been in Proposal stage for 18 days (average: 7). 73% of deals that stall here are lost." | Feature |
| **Competitive Intelligence** | Auto-detect competitor mentions in emails, meeting notes, web searches. Surface battle cards. | Feature |
| **Deal Similarity** | "This deal is similar to 5 previous deals. Average close time: 34 days. Win rate: 62%." | ⚠️ Possible |
| **Revenue Impact Forecast** | "If this deal closes, your Q2 target is 87% achieved. If it slips, you're at 71%." | Feature |
| **Three Brains Deal Score** | Independent AI assessment vs rep's gut feel. "You say 80% likely. Three Brains says 45%. Here's why..." | ✅ Patent candidate |
| **Commitment Tracker** | Every promise made by either party, extracted from meeting notes and emails. Status: kept/broken/pending. | ✅ Novel |

### 4.4 Sales Stages (Customisable)
Default stages for ANZ SMB:
1. **Prospect** — Identified, not yet contacted
2. **Discovery** — First conversation, needs analysis
3. **Qualification** — Budget, authority, need, timing confirmed
4. **Proposal** — Quote/proposal delivered
5. **Negotiation** — Terms being discussed
6. **Verbal Commitment** — Handshake, awaiting paperwork
7. **Closed Won** — Deal done, invoice generated
8. **Closed Lost** — Deal lost, autopsy triggered

Each stage has: entry criteria, exit criteria, required activities, maximum days before stall alert.

---

## 5. Territory Management

### 5.1 Territory Structure
| Level | Example |
|---|---|
| **Region** | ANZ, APAC, Global |
| **State/Territory** | NSW, VIC, QLD, WA, SA, TAS, NT, ACT, NZ-NI, NZ-SI |
| **Postcode Band** | 2000-2099 (Sydney CBD), 3000-3099 (Melbourne CBD) |
| **Industry Vertical** | Technology, Healthcare, Manufacturing, Professional Services |
| **Named Accounts** | Specific companies assigned to specific reps |

### 5.2 Territory Intelligence

| Feature | Description |
|---|---|
| **Territory Map** | Interactive map showing all accounts, deals, travel routes by territory |
| **Performance Comparison** | Side-by-side territory metrics: pipeline, revenue, win rate, average deal size |
| **Capacity Planning** | "Rep A has 42 active deals (capacity: 35). Rep B has 18. Rebalance recommended." |
| **Carbon-Optimised Routing** | "If you move these 3 accounts from Rep A (Wollongong) to Rep B (Parramatta), total travel carbon drops 23%." |
| **Territory Handoff** | When reps change territories: automated handoff workflow with warm intro templates, deal transfer, relationship history preservation |

---

## 6. Sales Sequences & Cadences

### 6.1 Multi-Channel Sequences
| Channel | Capabilities |
|---|---|
| **Email** | Templates, personalisation tokens, A/B testing, send-time optimisation |
| **SMS** | Via TextBee.dev integration. Personalised. Compliance-aware (opt-in tracking). |
| **Phone** | Call task with suggested script, talking points from Three Brains |
| **LinkedIn** | Connection request, InMail, post engagement — task-based (manual execution, tracked) |
| **Voice Note** | ElevenLabs-generated personalised audio message via ELAINE |
| **Direct Mail** | Task: send handwritten note or gift. Tracked. |

### 6.2 Sequence Intelligence

| Feature | Description |
|---|---|
| **A/B Testing** | Test email subject lines, send times, channel order |
| **Optimal Sequence** | AI recommends sequence order based on contact's Channel DNA |
| **Fatigue Detection** | "Sarah has received 5 touches in 10 days. She's disengaging. Pause and wait 7 days." |
| **Reply Detection** | Auto-detect replies and pause sequence. Route to human. |
| **Sentiment Analysis** | "Sarah's reply sentiment is negative. Don't auto-continue. Flag for human review." |
| **Performance Analytics** | Open rates, reply rates, meeting booked rates — per sequence, per step, per rep |

---

## 7. Quoting, Proposals & CPQ

### 7.1 Product Catalog
| Feature | Description |
|---|---|
| **Products** | Name, SKU, description, category, images |
| **Pricing** | List price, cost price, margin, currency (AUD default) |
| **Price Books** | Multiple price books per region, customer tier, volume |
| **Bundles** | Pre-configured bundles with discounted pricing |
| **Subscriptions** | Monthly/annual/custom billing periods |
| **Usage-Based** | Metered pricing with tier thresholds |

### 7.2 Quote Builder
| Feature | Description | Ripple Intelligence |
|---|---|---|
| **Drag-Drop Builder** | Add products, adjust quantities, apply discounts | Real-time margin calculator |
| **Discount Approval** | Configurable thresholds: >10% needs manager, >20% needs director | Automated workflow with Slack/email notification |
| **Template Library** | Branded quote templates. AMTL design system. | Multiple templates per industry/deal type |
| **E-Signature** | Built-in or DocuSign/Adobe Sign integration | Track: viewed, signed, declined |
| **Quote Tracking** | "Sarah viewed the quote for 4 min. Spent 2 min on pricing page." | Alert: "Quote viewed — call now?" |
| **Versioning** | Full version history. Compare versions side-by-side. | "Version 3 has 12% lower margin than Version 1. Are you sure?" |
| **PDF/Link** | Generate PDF or shareable web link | Web link has analytics: time spent, pages viewed |

### 7.3 Proposal Generator
| Feature | Description |
|---|---|
| **AI-Generated Proposals** | ELAINE drafts proposal from deal context + product selection + company research |
| **Content Library** | Reusable sections: About Us, Case Studies, Methodology, Terms |
| **Personalisation** | Auto-insert: contact name, company name, industry-specific examples, relevant case studies |
| **Competitor Positioning** | Auto-insert battle card content if competitor detected on deal |
| **Approval Workflow** | Route for review before sending |
| **Send & Track** | Email or link. Track opens, page views, forwards. |

**Ripple Innovation:** "Smart Pricing" — AI suggests optimal price point based on deal similarity analysis, competitor pricing intelligence, and customer's payment history (from Genie). "Deals like this close 28% faster at $X price point."

---

## 8. Contract Management

### 8.1 Contract Lifecycle
| Stage | Features |
|---|---|
| **Draft** | Template-based generation. Auto-populate from deal record. Clause library. |
| **Review** | Internal review workflow. Track changes. Version comparison. |
| **Negotiate** | External collaboration: customer can comment/suggest changes via secure portal |
| **Approve** | Multi-level approval with configurable rules (value thresholds, non-standard terms) |
| **Sign** | E-signature (built-in or DocuSign/Adobe Sign) |
| **Active** | Contract stored, linked to deal + account. Key dates tracked. |
| **Renew/Amend** | Renewal reminders (90/60/30 days). Amendment workflow. Auto-generate renewal quote. |
| **Expire/Terminate** | Expiry alerts. Termination workflow with exit checklist. |

### 8.2 Contract Intelligence

| Feature | Description |
|---|---|
| **Clause Library** | Pre-approved clauses with compliance ratings. "This clause is ISO 27001 compliant." |
| **Risk Scoring** | AI analyses contract terms for risk: non-standard clauses, unfavourable payment terms, excessive liability. |
| **Obligation Tracking** | Extract obligations from contract text. Track fulfilment. Alert on approaching deadlines. |
| **Auto-Renewal Detection** | "This contract auto-renews in 45 days. Customer satisfaction score: 72% (amber). Review before renewal." |
| **Revenue Recognition** | Link contract terms to revenue schedule. Feed to Genie for ASC 116/IFRS 15 compliance. |
| **Contract Search** | Full-text search across all contracts. "Find all contracts with indemnity clauses over $1M." |

**Ripple Innovation:** "Contract Health Score" — composite of: days to sign (vs benchmark), number of negotiation rounds, clause deviation from standard, payment term deviation. "Healthy contracts close in 14 days. This one is at 32 days — investigate."

---

## 9. Sales Forecasting & Revenue Intelligence

### 9.1 Forecasting
| Feature | Description |
|---|---|
| **Weighted Pipeline** | Deal value × probability at each stage |
| **AI Forecast** | Three Brains probability vs rep-stated probability. "AI predicts $420K this quarter. Your reps predict $580K. Historical accuracy: AI is closer 73% of the time." |
| **Scenario Planning** | Best case / commit / worst case with deal-level toggles |
| **Forecast Categories** | Pipeline, Best Case, Commit, Closed. Configurable per stage. |
| **Forecast Hierarchy** | Rep → Manager → Director → VP. Roll-up with override tracking. |
| **Forecast Accuracy Tracking** | "Your forecast accuracy last quarter: ±14%. Industry benchmark: ±18%. You're improving." |

### 9.2 Revenue Intelligence (Clari-Style)

| Feature | Description |
|---|---|
| **Pipeline Inspection** | Deal-by-deal review with AI risk flags. "3 deals at risk this quarter." |
| **Deal Velocity** | Days in each stage vs benchmark. "This deal is 2x slower than average at this stage." |
| **Engagement Score** | Contact engagement level on each deal. "Decision maker hasn't engaged in 21 days." |
| **Coverage Ratio** | "You need 3x pipeline to hit target. Currently at 2.4x. Gap: $180K in pipeline needed." |
| **Win Rate Analysis** | By rep, territory, product, deal size, industry. "You win 78% of deals under $50K but only 34% over $100K." |
| **Revenue Leakage** | "12 deals worth $340K were lost to 'no decision' this quarter. 8 had stalled in Proposal." |

---

## 10. Sales Performance & Coaching

### 10.1 Rep Performance
| Metric | Description |
|---|---|
| **Activity Metrics** | Calls, emails, meetings, proposals per day/week/month |
| **Outcome Metrics** | Deals won, revenue, win rate, average deal size, cycle time |
| **Efficiency Metrics** | Revenue per activity, meetings-to-close ratio, quote-to-close ratio |
| **Target vs Actual** | Visual gauge with trend. Daily/weekly/monthly targets. |
| **Leaderboard** | Gamified. Configurable metrics. Optional anonymisation. |

### 10.2 Sales Coaching

| Feature | Description |
|---|---|
| **Cognitive Bias Detection** | "You consistently overestimate close probability by 18%. Recalibrate." |
| **Methodology Coaching** | Embed SPIN, Sandler, Challenger — localised for ANZ. "You skipped the pain question. Ask before presenting solution." |
| **Deal Review** | Manager reviews deal with AI-generated summary: risks, next actions, missing stakeholders |
| **Conversation Intelligence** | Meeting transcript analysis: talk ratio, question count, competitor mentions, objection handling score |
| **Skill Gap Analysis** | "Your discovery calls are strong but your negotiation close rate is below team average. Suggested training: [link]." |

---

## 11. Commission & Incentive Management

### 11.1 Commission Plans
| Feature | Description |
|---|---|
| **Plan Builder** | Base + commission %. Tiered (accelerators above quota). Split deals. |
| **Multi-Currency** | AUD, NZD, USD with exchange rate management |
| **Quota Management** | Set, track, adjust quotas per rep/territory/product |
| **Commission Calculation** | Auto-calculate on deal close. Preview before finalisation. |
| **Payout Integration** | Feed to Genie for payroll processing |
| **Dispute Resolution** | Rep can flag commission discrepancy. Workflow for review. |
| **What-If Calculator** | "If I close this deal, my commission this quarter will be $X." |

---

# PART C: PRIVACY & TRANSPARENCY

## 12. Transparency Portal — "My Data" (RIPPLE EXCLUSIVE)

### The Idea
Mani's insight: "If any contact asks for information the user has about them, they should get it easily and quickly."

This is brilliant. Under GDPR (Article 15), CCPA, and Australia's Privacy Act, individuals have the right to access data held about them. No CRM makes this easy. Most require a manual, weeks-long process involving legal teams.

**Ripple makes it one-click.**

### 12.1 How It Works

**For the Ripple User (your team):**
1. Contact asks: "What data do you have about me?"
2. Rep clicks **"Generate Transparency Report"** button on contact record
3. Ripple auto-compiles everything:
   - All contact fields
   - All communication history (emails, calls, meetings)
   - All notes and documents
   - All deal associations
   - All enrichment sources used
   - Consent records (when, what, how)
   - Data processing purposes
   - Third-party sharing log
4. Report generated as branded PDF or secure web link
5. Rep reviews (30-second scan for anything sensitive)
6. One-click send to contact via secure link
7. Full audit trail: who requested, when, who reviewed, when sent

**For the Contact (self-service option):**
1. Contact receives email link to **Ripple Privacy Portal**
2. Verifies identity (email OTP or photo ID upload)
3. Views their data in clean, readable format
4. Can request: correction, deletion, export, consent withdrawal
5. All requests logged and routed to Ripple user for action

### 12.2 Privacy Rights Automation

| Right | GDPR Article | Ripple Automation |
|---|---|---|
| **Right of Access** | Art. 15 | One-click Transparency Report. Auto-compile all data. |
| **Right to Rectification** | Art. 16 | Contact can flag incorrect data. Routed to owner for update. |
| **Right to Erasure** | Art. 17 | "Forget Me" button. Erases all personal data, preserves anonymised analytics. Audit trail of deletion. |
| **Right to Data Portability** | Art. 20 | Export all data in machine-readable format (JSON, CSV). |
| **Right to Object** | Art. 21 | Contact can opt-out of processing. Auto-updates consent records + suppression lists. |
| **Right to Restrict Processing** | Art. 18 | Data frozen — visible but not usable in sequences, campaigns, or AI processing. |
| **Consent Management** | Art. 7 | Granular consent tracking: what they consented to, when, via which channel, which version of privacy policy. |
| **Automated Decision Disclosure** | Art. 22 | If AI scoring is used, explain in plain language: "We use AI to prioritise our response time. Your score is based on..." |

### 12.3 Privacy Dashboard (Internal)

| Metric | Description |
|---|---|
| **Consent Coverage** | % of contacts with valid, current consent |
| **DSAR Volume** | Data subject access requests received / fulfilled / overdue |
| **Data Freshness** | % of contacts verified in last 12 months |
| **Retention Compliance** | Contacts past retention period flagged for review |
| **Processing Lawfulness** | Breakdown by legal basis (consent, legitimate interest, contractual necessity) |
| **Third-Party Sharing Log** | Which enrichment providers received data and when |

### 12.4 Patent Candidate

**"Automated CRM Data Subject Access Request Fulfilment with One-Click Transparency Report Generation"**

A system that, upon request, auto-compiles all personal data held across CRM modules (contacts, communications, deals, enrichment, AI scoring) into a branded, human-readable report, with identity verification, review workflow, secure delivery, and full audit trail. Includes self-service portal for data subjects to view, correct, export, or request deletion of their data.

**Why it's novel:** No shipping CRM product offers one-click DSAR fulfilment with a self-service portal for data subjects. Salesforce requires admin intervention. HubSpot requires manual compilation. Dynamics requires Power Automate workflows. This is automated, branded, and built into the CRM natively.

---

# PART D: INTEGRATION & INFRASTRUCTURE

## 13. Email & Calendar Integration

### 13.1 Email
| Feature | Description |
|---|---|
| **Gmail Sidebar** | Chrome extension: view contact record, log email, create deal — without leaving Gmail |
| **Outlook Add-in** | Same features in Outlook desktop and web |
| **Email Tracking** | Opens, clicks, replies, forwards. Notification in real-time. |
| **Email Logging** | Auto-log all emails with matched contacts (configurable: all/selected/none) |
| **Email Templates** | Library with personalisation tokens. AI-generated suggestions. |
| **Email Sequences** | Multi-step automated cadences (see Section 6) |
| **Send-Time Optimisation** | AI recommends best send time per contact based on historical open patterns |
| **Shared Inbox** | Team email (sales@, info@) with assignment and routing |

### 13.2 Calendar
| Feature | Description |
|---|---|
| **Bidirectional Sync** | Google Calendar / Exchange. Two-way: create/update/delete. |
| **Meeting Scheduler** | Shareable booking link (like Calendly but built-in). "Book a time with Sarah." |
| **Intentional Calendar** | When meeting is created: "Which deal is this for? What outcome do you want?" Metadata survives round-trip sync. |
| **Meeting Prep** | Prep Me button: auto-generate brief from contact history, deal status, recent communications, news. |
| **Meeting Follow-Up** | Follow Me: "Meeting with Sarah ended 5 min ago. Log notes? Create actions?" |
| **Round-Robin Booking** | Distribute meetings across team based on availability and capacity |
| **Timezone Intelligence** | Auto-detect attendee timezones. Warning if meeting is outside business hours for any attendee. |

## 14. Telephony & Communication

| Feature | Description |
|---|---|
| **Click-to-Call** | One-click dial from contact record. Timezone-aware: "Good time to call" indicator. |
| **Call Logging** | Duration, outcome (connected/voicemail/no answer), notes. Auto-logged. |
| **Call Recording** | With consent (two-party consent for AU). Stored, searchable, transcribable. |
| **VoIP Integration** | Twilio / Plivo / RingCentral / Dialpad integration. Choose your provider. |
| **SMS** | TextBee.dev integration. Send/receive SMS from contact record. Templates. Compliance tracking. |
| **WhatsApp Business** | Send/receive via WhatsApp Business API. Logged to timeline. |
| **Voicemail Drop** | Pre-recorded voicemail. One-click drop during call. |
| **Power Dialer** | Auto-dial through call list. Log outcomes. Next contact queued. |

## 15. Mobile

### 15.1 Progressive Web App (PWA)
- Installable on iOS and Android
- Offline-first: full functionality without connectivity, sync when connected
- Dark mode native
- Biometric authentication

### 15.2 Mobile-Specific Features
| Feature | Description |
|---|---|
| **Voice CRM** | "Log meeting with Sarah at Bunnings. Discussed delivery timelines. Next step: send quote by Friday." → Structured record created. |
| **Business Card Scanner** | OCR → auto-create contact with enrichment |
| **Nearby Contacts** | Map view: "3 contacts within 2 km of your current location" |
| **Quick Log** | Meeting, call, note — all loggable in <30 seconds |
| **Prep Me** | Pre-meeting brief delivered as push notification or audio briefing |
| **Travel Companion** | Directions, parking notes, office location, receptionist name (if stored) |
| **Today View** | Meetings, tasks, deals requiring action — one screen |
| **Offline Mode** | Full read/write access offline. Conflict resolution on sync. |

### 15.3 Contextual Commute Briefing (Ripple Exclusive)
"You have a 22-minute train ride to your meeting with Sarah. Here's a 20-minute audio briefing: Sarah's company news, your last 3 emails, the competitor's latest press release, and suggested talking points."

Dynamically sized to match travel duration. Generated by ELAINE via Ollama. Delivered as audio (ElevenLabs) or text.

**Patent Candidate:** "Context-Aware Commute Learning Injection — dynamically generating audio learning playlists sized to match estimated travel time to calendar events."

---

# PART E: AI & MACHINE LEARNING

## 16. The Intelligence Stack

### 16.1 Three Brains Decision Engine
| Brain | Data Sources | Output |
|---|---|---|
| **Logic** | Deal data, ICP scoring, firmographics, pipeline rules | Deterministic score + explanation |
| **Evidence** | Activity history, engagement metrics, win/loss patterns | Probabilistic score + supporting data |
| **Instinct** | Sentiment analysis, social signals, timing patterns, relationship decay | LLM-generated insight + confidence |

**Combined:** Weighted recommendation with traffic-light simplicity. Adaptive weighting per contact based on outcome feedback.

### 16.2 ELAINE CRM Module
| Capability | Description |
|---|---|
| **Morning Briefing** | "Today you have 3 meetings. 2 deals need attention. Sarah's trust is decaying — call her. Your forecast is 12% behind target." |
| **Proactive Alerts** | "Deal stalled 18 days. Contact went quiet 21 days. Competitor mentioned in industry news." |
| **Task Execution** | Draft emails, schedule meetings, update deal stages, generate reports — with approval gates. |
| **Voice Interface** | "ELAINE, what should I focus on today?" → Spoken response via ElevenLabs. |
| **Multi-Step Workflows** | "When deal moves to Negotiation: generate contract draft, notify legal, schedule internal review, create follow-up task." |

### 16.3 AI Features Across Modules

| Feature | Where | What |
|---|---|---|
| **Auto-Enrichment** | Contacts, Accounts | Auto-fill from ABR, LinkedIn, web |
| **Predictive Lead Scoring** | Leads | ML model trained on historical conversions |
| **Deal Probability** | Opportunities | AI probability independent of rep estimate |
| **Sentiment Analysis** | Emails, Meetings | Track sentiment trend per contact |
| **Email Generation** | Sequences, Follow-ups | AI-drafted with personalisation |
| **Meeting Summary** | Meeting Intelligence | Auto-summarise transcript into structured notes |
| **Action Extraction** | Meetings, Emails | Extract commitments and deadlines |
| **Duplicate Detection** | Contacts, Accounts | Fuzzy matching with confidence score |
| **Churn Prediction** | Accounts | Relationship decay + payment patterns + engagement decline |
| **Upsell Detection** | Accounts | Usage patterns + growth signals + role changes |
| **Content Recommendation** | Sequences | "Send this case study — Sarah's industry and deal size match." |
| **Conversation Coaching** | Call/Meeting Review | Talk ratio, question count, next steps mentioned, objection handling |
| **Forecast Adjustment** | Forecasting | Auto-adjust based on deal health signals |
| **Carbon Calculation** | Travel Intelligence | Auto-calculate emissions per visit |
| **Bias Detection** | Rep Coaching | Flag cognitive biases in deal assessment |

### 16.4 Privacy-First AI
- All AI processing via local Ollama (privacy-first — data never leaves the machine)
- No cloud API fallback for customer data processing
- AI decisions are explainable: every score has a "why"
- AI Audit Trail: every AI action logged with input, output, confidence, and model version
- Contact can request AI decision explanation (GDPR Art. 22 compliance)

---

# PART F: REPORTING & DASHBOARDS

## 17. Reporting

### 17.1 Pre-Built Reports
| Category | Reports |
|---|---|
| **Pipeline** | Pipeline by stage, by rep, by territory, by product. Pipeline velocity. |
| **Revenue** | Closed won, forecast vs actual, MoM/QoQ/YoY trends |
| **Activity** | Calls, emails, meetings per rep. Activity-to-outcome ratios. |
| **Lead** | Lead sources, conversion rates, time to convert, scoring accuracy |
| **Account** | Account health, revenue per account, expansion/contraction |
| **Travel** | Total km, cost, carbon by rep/territory/account. Visits per deal. |
| **Meeting** | Frequency, duration, actions created vs completed, meeting-to-close correlation |
| **Commission** | Earned, pending, paid. By rep, territory, product. |
| **Privacy** | DSAR volume, consent coverage, data freshness, retention compliance |

### 17.2 Custom Report Builder
- Drag-and-drop field selection
- Filter by any field combination
- Group, pivot, sort
- Visualisation: bar, line, pie, funnel, scatter, heatmap, gauge, table
- Schedule: daily/weekly/monthly email delivery
- Export: PDF, Excel, CSV
- Share: link, embed, dashboard

### 17.3 Dashboard Design
- Pre-built dashboards: Sales Overview, Pipeline Health, Rep Performance, Territory, Forecast
- Custom dashboards: unlimited, shareable, role-based
- Widgets: charts, metrics, leaderboards, activity feeds, AI alerts
- Real-time refresh
- Mobile-responsive
- **Design principle:** Every dashboard should look like a Bloomberg terminal — dense with information but visually elegant. No wasted space. No ugly default charts.

---

# PART G: MARKETING CONNECTION

## 18. Spark Integration (Three Marketing Brains)

| Integration | Description |
|---|---|
| **Lead Flow** | Marketing qualified leads flow from Spark → Ripple automatically |
| **Campaign Attribution** | Multi-touch attribution visible on contact and deal records |
| **Content Engagement** | Spark content downloads, webinar attendance, ad clicks — all logged to Ripple timeline |
| **Audience Sync** | Ripple segments available as Spark audiences for targeting |
| **ROI Reporting** | Campaign → Lead → Deal → Revenue. Full funnel attribution. |
| **ABM Coordination** | Target account lists shared between Spark and Ripple. Coordinated outreach. |

---

# PART H: WORKFLOW & AUTOMATION

## 19. Automation Engine

### 19.1 Trigger → Condition → Action

| Triggers | Conditions | Actions |
|---|---|---|
| Deal stage change | Value > $X | Send email |
| Lead created | Source = web | Assign to rep |
| Email opened | Contact = Decision Maker | Create task |
| Meeting completed | Sentiment = negative | Alert manager |
| Quote viewed | Time on pricing > 2 min | Notify rep |
| Contract expiring | Days until expiry < 90 | Start renewal sequence |
| Relationship health drops | Score < 40 | Escalate to manager |
| Payment overdue (Genie) | Days > 30 | Flag on deal |

### 19.2 ELAINE Orchestration
Multi-step workflows with approval gates. Not just "if X then Y" — agentic sequences that adapt based on outcomes.

Example: "When deal moves to Negotiation → Generate contract draft → Route to legal for review → If approved, send to customer → Track views → If not signed in 7 days, send reminder → If not signed in 14 days, alert rep → If signed, create invoice in Genie."

---

# APPENDIX: PATENT PORTFOLIO SUMMARY

| # | Patent Title | Category | Status |
|---|---|---|---|
| 1 | Channel DNA Predictor — per-contact adaptive channel/time optimisation | AI | ✅ File now |
| 2 | ELAINE Orchestration Architecture — agentic CRM task execution with approval gates | AI | ✅ File now |
| 3 | Carbon-Aware Deal Economics — carbon cost in discount approval and territory routing | Sustainability | ✅ File now |
| 4 | Dynamic Presence Optimisation — ROI of physical vs virtual meeting based on trust decay | Sales Intelligence | ✅ File now |
| 5 | Automated DSAR Fulfilment — one-click transparency report with self-service portal | Privacy | ✅ File now |
| 6 | Context-Aware Commute Learning Injection — audio prep sized to travel time | Mobile | ✅ File now |
| 7 | Three Brains Decision Engine — tri-vector adaptive scoring with outcome feedback | AI | ⚠️ After implementation |
| 8 | Meeting Causality Engine — meeting pattern → deal outcome causal model | Analytics | ⚠️ After implementation |
| 9 | Relationship Value Quantification — dollar-impact scoring of relationship nodes | Graph | ⚠️ After implementation |
| 10 | Commitment Tracker — AI extraction and fulfilment tracking of bilateral promises | Sales Intelligence | ⚠️ After implementation |

---

*"The market does not need another good CRM. The market needs a fundamentally different way of thinking about commercial relationships. Ripple is that difference."*

*— Thalaiva, 12 February 2026*

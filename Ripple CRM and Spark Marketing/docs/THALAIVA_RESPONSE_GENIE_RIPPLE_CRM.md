# Thalaiva Response — 12 February 2026
## Genie Gaps, Ripple v3 Additions, and CRM Competitive Intelligence

---

## 1. GENIE — FLEET & ASSET REGISTER STATUS

Good news: both **Fleet** and **Asset Register** exist in the spec and the database schema. They're not missing — they're in different stages of completion.

### Asset Register (Fixed Assets & Depreciation)
- **Module #16** in the registry: `fixed_assets` — marked ✅ ON
- **Database schema:** ✅ Complete (Phase 2) — tables for fixed_assets with depreciation, disposal, location tracking, condition columns
- **Frontend:** ✅ Built in Phase 3 — "Asset Register (enhanced with 10+ columns, depreciation, warranty, condition)" is listed as module #5 of the 9 completed frontends
- **Achievement:** ASSET_TRACKER (15 points) exists
- **Verdict:** This one is DONE. Both backend and frontend exist.

### Fleet Manager (Fleet & Vehicle Log)
- **Module #21** in the registry: `fleet` — marked ✅ ON  
- **Database schema:** ✅ Created (Phase 2) — `fleet_vehicles` and `fleet_logs` tables referenced in audit, though listed under "Tables Not Yet Verified" (Section 20)
- **Frontend:** ❌ NOT BUILT — Listed as module #17 of the "Build These" list in Claude Code Instructions. Fleet Manager is one of the 8 modules that have backend+API but no frontend yet
- **Verdict:** Backend exists, frontend missing. This is a Week 4-type task for Guruve.

### What To Tell Guruve About Genie

> *"Run a full schema introspection on genie.db to verify all tables exist. Specifically check: fleet_vehicles, fleet_logs, fixed_assets. Then compare against the GENIE_COMPLETE_AUDIT_FEB2026.md module registry (44 modules) and the Claude Code Instructions (17 frontends, 9 built, 8 pending). The blocking issue is the Phase 4 analytics_widgets column name bug — fix that first before building any new frontends."*

### Summary of Missing Genie Frontends (Backend Exists)

| # | Module | Priority |
|---|--------|----------|
| 1 | Journal Entries | High — core bookkeeping |
| 2 | AR Aging | High — debtor management |
| 3 | AP Aging | High — payables management |
| 4 | Loan Tracker | Medium |
| 5 | Petty Cash | Medium |
| 6 | Receipt Vault | Medium — needs OCR via Ollama |
| 7 | Inventory | Medium |
| 8 | **Fleet Manager** | Medium — this is the one you noticed |

Plus the Phase 4 gap-fill tables (analytics_snapshots, forecast_engine, custom_modules, etc.) that crashed before creation.

---

## 2. RIPPLE v3 — PROPOSED ADDITIONS

Your Ripple v3 spec already has the foundations for some of these ideas. Here's what exists and what's new:

### 2.1 Travel Intelligence Panel (NEW)

**What exists in v3:** The Address field has "Map pin with travel time. Timezone derived. Directions button." — but it's basic.

**Your vision expands this into a Travel Intelligence Panel** that appears next to or below the contact address. Here's the proposed specification:

#### Travel Intelligence Panel — Contact Record

| Field / Element | Specification |
|----------------|---------------|
| **Google Maps Link** | One-click button: "Get Directions." Opens Google Maps in browser with pre-populated destination (contact's address) and user's office as origin. Uses URL format: `https://www.google.com/maps/dir/?api=1&origin={user_office}&destination={contact_address}`. No API key required — just URL construction. |
| **Distance (km)** | User-editable field. Pre-populate label "Distance:" with empty input. After clicking "Get Directions" and checking Google Maps, user types in the km. Alternatively, if Google Maps Directions API is integrated later, auto-fill. |
| **Estimated Travel Cost** | User-editable. Fields: Transport Mode dropdown (Car / Uber / Taxi / Train / Bus / Walk / Bike), Estimated Cost ($), Toll Cost ($). If "Car" selected: show km × ATO rate ($0.88/km for 2025-26) as default estimate. If "Uber" selected: show link to Uber fare estimator with pre-populated pickup/dropoff. |
| **Tolls** | Checkbox: "Route includes tolls?" If yes, editable toll cost field. For Sydney: note common toll roads (M2, M5, M7, Lane Cove Tunnel, Cross City Tunnel, Harbour Bridge/Tunnel, WestConnex). |
| **Public Transport** | Button: "Check Train/Bus." Opens TripPlanner (transportnsw.info) or Google Maps transit mode with pre-populated addresses. For other states: links to PTV (VIC), TransLink (QLD), Metrolink (SA). |
| **Carbon Emissions** | Auto-calculated based on transport mode and distance. Display as: "🌱 This trip generates approximately X.X kg CO₂." Calculation: Car = 0.21 kg CO₂/km (average AU passenger vehicle), Uber/Taxi = 0.25 kg CO₂/km (includes deadheading), Train = 0.04 kg CO₂/km (AU average electric rail), Bus = 0.09 kg CO₂/km. Show comparison: "That's equivalent to X smartphone charges" or "X trees absorb this in a day." |
| **Carbon Summary** | Monthly/quarterly view on contact record: "Total travel emissions to visit [Contact]: X.X kg CO₂ across Y visits." Company-level rollup on Company record. |
| **Travel History** | Log each visit: date, mode, km, cost, emissions. Builds over time. Shows: "You've visited Sarah 4 times this quarter. Total: 120km, $48 tolls, 25.2 kg CO₂." |

**Design principle:** We don't need Google Maps API for v1. Just construct URLs that open Google Maps with pre-populated addresses. Let the user enter the data after checking. The intelligence comes from tracking it over time and calculating emissions automatically.

**Future enhancement (v2):** Google Maps Directions API for auto-population of distance, duration, tolls. But that requires an API key and costs — defer until Ripple has paying customers.

### 2.2 Meeting Intelligence Hub (NEW — Granola/Otter Alternative)

**What exists in v3:** "Prep Me Button" for pre-meeting briefs, "Auto-log calls, emails, meetings. AI captures notes." — but no detailed meeting notes system.

**Your vision: every meeting gets structured notes, actions, and follow-ups — either captured in Ripple or imported from tools like Otter.ai, Fireflies.ai, Granola, etc.**

#### Meeting Record — Specification

| Field / Element | Specification |
|----------------|---------------|
| **Meeting Record** | Created automatically when: (a) calendar event with contact attendee detected, (b) user clicks "Log Meeting" on contact, (c) imported from external tool. Fields: Date/time, duration, attendees (linked contacts), location/virtual, meeting type (Discovery / Demo / Review / Negotiation / Support / Other). |
| **Meeting Notes** | Rich text editor. Structured template with sections: Key Discussion Points, Decisions Made, Action Items, Next Steps, Sentiment/Mood. AI can auto-summarise if raw transcript provided. |
| **Action Items** | Extracted from notes (AI-assisted or manual). Each action: description, owner (contact or team member), due date, status (Open / In Progress / Done / Overdue). Actions sync to ELAINE task list and appear on contact timeline. |
| **Email Import** | Dedicated email address: `meetings@[domain]` or per-user address. User forwards meeting summary from Otter.ai, Fireflies, Granola, Tactiq, Fellow, etc. Ripple parses the email: (a) matches attendee names/emails to contacts, (b) extracts action items (looks for patterns: "Action:", "TODO:", "Follow up:", numbered lists), (c) creates Meeting Record with imported content. |
| **Otter.ai Integration** | If user has Otter.ai: webhook or email forward. Otter sends transcript + summary → Ripple creates Meeting Record. Map Otter participants to Ripple contacts. |
| **Granola-Style AI Summary** | If raw transcript is pasted or imported: Ask Genie (local Ollama) processes it into structured format: Summary (3-5 bullet points), Decisions, Actions, Sentiment. Privacy-first — all processing local. |
| **Prep Me + Follow Me** | **Prep Me** (existing): Pre-meeting brief. **Follow Me** (NEW): Post-meeting prompt: "Meeting with Sarah ended 5 mins ago. Log notes? Create follow-up actions?" Auto-triggers if calendar event with contact just ended. |
| **Meeting Timeline** | All meetings appear on: contact timeline, deal timeline, company timeline. Searchable. "Show me all meetings with TechCo in Q4." |
| **Meeting Analytics** | Per contact: meeting frequency, average duration, actions generated vs completed. Per deal: meetings to close, average meeting-to-close time. Per user: meetings per week, action completion rate. |

**Integration approach:** Don't build a transcription engine. Let users use whatever tool they prefer (Otter, Fireflies, Granola, Teams transcription, Zoom transcription) and import via email forward or paste. Ripple's job is to structure, store, link to contacts, and extract actions.

### 2.3 Where These Fit in Ripple v3

Add as new sections to the spec:

- **Section 4.X: Travel Intelligence Panel** — under Contact Record (Part A)
- **Section 6.X: Meeting Intelligence Hub** — new section in Part A (or expand Section 12.2 Automation Principles)
- **Dashboard widget:** "This Week's Travel: X meetings, Y km, $Z cost, W kg CO₂"
- **Company record rollup:** Total travel cost and emissions per company

---

## 3. CRM COMPETITIVE INTELLIGENCE — FOR LLM FEEDBACK

Here's what the top CRMs offer across Contact Management and Sales Force Automation. Use this as the benchmark document to give to other LLMs alongside the Ripple v3 spec.

### 3.1 Contact Management — Feature Comparison

| Feature | Salesforce | HubSpot | Dynamics 365 | Zoho CRM | Ripple v3 |
|---------|-----------|---------|-------------|---------|-----------|
| **Basic contact fields** (name, email, phone, address, title) | ✅ Standard | ✅ Standard | ✅ Standard | ✅ Standard | ✅ + intelligence on every field |
| **Custom fields** | ✅ Unlimited | ✅ Up to 1000 | ✅ Via Power Platform | ✅ Custom modules | ✅ + auto-enrichment |
| **Contact-Account association** | ✅ Many-to-one | ✅ Many-to-many | ✅ Many-to-one | ✅ Standard | ✅ + cross-company graph |
| **Activity timeline** (calls, emails, meetings, notes) | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ + AI narrative |
| **Contact hierarchy** (reports-to chains) | ✅ Via lookup | ⚠️ Limited | ✅ Org chart | ⚠️ Limited | ✅ Stakeholder maps |
| **Duplicate detection** | ✅ Built-in | ✅ Auto-merge | ✅ AI-based | ✅ Basic rules | ✅ AI dedup |
| **Data enrichment** (auto-fill company data) | ✅ Einstein (paid add-on) | ✅ 20M+ businesses free | ✅ LinkedIn Sales Nav | ✅ Zia enrichment | ✅ Snitcher + Identity Atlas + ABR + Echo |
| **Social media integration** | ✅ Social Studio (being retired) | ✅ Social inbox | ⚠️ Via LinkedIn only | ✅ Social tab | ✅ Editable + enriched per platform |
| **Email tracking** (opens, clicks) | ✅ Standard | ✅ Free tier | ✅ Standard | ✅ Standard | ✅ + response rate, best send time |
| **Click-to-call** | ✅ With telephony partner | ✅ Built-in | ✅ With Teams | ✅ Built-in | ✅ + timezone-aware "Call now?" |
| **Timezone awareness** | ⚠️ Manual field | ⚠️ Manual field | ⚠️ Manual field | ⚠️ Manual field | ✅ Auto-derived, contact-level clock |
| **Contact lifecycle stages** | ✅ Lead → Contact → Account | ✅ Lifecycle stages | ✅ Lead → Opportunity → Customer | ✅ Standard stages | ✅ 6-stage with colour-coded badges |
| **Relationship mapping** (cross-company) | ⚠️ Account relationships basic | ❌ No native | ⚠️ Via stakeholder maps on deals | ⚠️ Basic | ✅ Patentable — cross-company web |
| **AI-powered insights** | ✅ Einstein GPT | ✅ Breeze Copilot | ✅ Copilot for Sales | ✅ Zia AI | ✅ Three Brains Decision Engine |
| **Communication preference detection** | ❌ | ❌ | ❌ | ❌ | ✅ Channel DNA (auto-detected) |
| **Contact anniversary/tenure** | ❌ | ❌ | ❌ | ❌ | ✅ Tenure badges + anniversary alerts |
| **Complaint history on contact** | ⚠️ Via Cases object | ✅ Via tickets | ✅ Via Case entity | ⚠️ Via support module | ✅ Embedded in contact with escalation |
| **Travel intelligence** | ❌ | ❌ | ❌ (Field Service has maps) | ❌ | ✅ NEW — distance, cost, carbon, history |
| **Meeting notes + actions** | ⚠️ Via Activities | ⚠️ Via notes | ✅ Via Activities | ⚠️ Basic notes | ✅ NEW — Granola-style structured notes with AI |

### 3.2 Sales Force Automation — Feature Comparison

| Feature | Salesforce | HubSpot | Dynamics 365 | Zoho CRM | Ripple v3 |
|---------|-----------|---------|-------------|---------|-----------|
| **Lead scoring** | ✅ Einstein Lead Scoring (AI) | ✅ Predictive scoring (Pro+) | ✅ AI-powered scoring | ✅ Zia prediction | ✅ Three-axis (Fit + Intent + Instinct) |
| **Lead routing** | ✅ Assignment rules | ✅ Automated rotation | ✅ Unified routing | ✅ Assignment rules | ✅ Territory + round-robin + AI |
| **Pipeline management** | ✅ Kanban + list | ✅ Visual pipeline | ✅ Business process flows | ✅ Blueprint + Kanban | ✅ Kanban + Forecast + Map view |
| **Opportunity management** | ✅ Full lifecycle | ✅ Deal records | ✅ Opportunity entity | ✅ Full deals module | ✅ + Win/Loss autopsy + competitive intel |
| **Proposal/quote generation** | ⚠️ Via CPQ (paid add-on) | ✅ Quotes (Sales Hub) | ✅ Quote entity | ✅ Inventory + quotes | ✅ Built-in with brand templates |
| **Sales sequences/cadences** | ✅ Sales Engagement (add-on) | ✅ Sequences (Pro+) | ✅ Sales accelerator | ✅ Cadences | ✅ Multi-channel with ELAINE |
| **Territory management** | ✅ Enterprise only | ❌ No native | ✅ Territory entity | ✅ Territory module | ✅ AU-state-based with postcode mapping |
| **Sales forecasting** | ✅ AI-powered | ✅ Forecasting tool | ✅ Predictive forecasting | ✅ Zia forecasting | ✅ Weighted + AI + scenario planning |
| **Commission tracking** | ⚠️ Via Incentive Compensation (add-on) | ❌ No native (partner apps) | ⚠️ Basic via custom entities | ⚠️ Via custom module | ✅ Built-in + Genie integration for payouts |
| **Account-Based Marketing (ABM)** | ✅ Via Pardot/MC | ⚠️ Target accounts (Enterprise) | ⚠️ Via Marketing module | ⚠️ Limited | ✅ Built-in with Snitcher + ICP scoring |
| **Performance analytics** | ✅ Einstein Analytics | ✅ Reports + dashboards | ✅ Copilot analytics | ✅ Reports | ✅ Target vs Actual + Morning Briefing |
| **Meeting prep/briefing** | ⚠️ Manual or Einstein | ❌ No native | ✅ Copilot meeting prep | ❌ | ✅ Prep Me button — automatic brief |
| **Next-best-action AI** | ✅ Einstein Next Best Action | ✅ Breeze AI suggestions | ✅ Copilot suggestions | ✅ Zia recommendations | ✅ AI-driven via Three Brains |

### 3.3 What Ripple v3 Has That NOBODY Else Does

These are genuine differentiators — features not available in any of the Big 4:

1. **Three Brains Decision Engine** — Logic + Evidence + Instinct combined into a single recommendation with traffic-light simplicity. No CRM does this.

2. **Cross-Company Relationship Graph** — Sarah at TechCo knows James at DataHouse. Visible, searchable, actionable. Salesforce has basic account relationships; nobody maps the human web across organisations.

3. **Channel DNA** — Auto-detected communication preferences ("Responds fastest on: Email (2.1hrs) > Phone (4hrs) > LinkedIn (2 days)"). Nobody auto-detects this.

4. **Timezone-Aware Everything** — Contact-level clocks, "Call now?" based on local time, meeting scheduler with timezone warnings. Other CRMs store timezone as a static field.

5. **Snitcher + Identity Atlas + Echo** — Four-layer enrichment (web visitor ID + business registry + shadow signals + AI profile). Other CRMs have one enrichment source, maybe two.

6. **Contact Anniversary & Tenure** — "3-year customer" badges, anniversary alerts, tenure-based pricing recommendations. Nobody does this.

7. **Travel Intelligence with Carbon Tracking** (NEW) — Distance, cost, emissions, history per contact. Nobody.

8. **Meeting Intelligence Hub** (NEW) — Import from Otter/Granola/any tool, AI-structured notes, auto-extracted actions. Salesforce and Dynamics have basic activity logging; nobody has structured meeting intelligence with AI summarisation from transcripts.

9. **Australian-First Design** — ABN auto-fill that populates 50 fields, ATO integration, AEST defaults, AUD formatting, state-based territories. Other CRMs treat Australia as an afterthought.

10. **ELAINE Orchestration** — No CRM has an AI Chief of Staff that executes tasks, not just recommends them.

### 3.4 What Ripple v3 Might Be Missing (For LLM Review)

Prompt for other LLMs:

> *"Review the Ripple v3 Product Specification against Salesforce Sales Cloud, HubSpot Sales Hub, Microsoft Dynamics 365 Sales, and Zoho CRM. Focus on: (a) Core contact management features Ripple might be missing, (b) Sales automation features that are table-stakes in 2026 but absent from Ripple, (c) Integration capabilities (email, calendar, telephony, marketing automation) that need attention, (d) AI features the competitors are shipping that Ripple should consider, (e) Mobile/field sales features, (f) Reporting and analytics gaps. Be specific about feature names and how competitors implement them."*

### 3.5 Key Areas for LLM Review

Things I'd specifically flag for other LLMs to scrutinise:

1. **Email integration depth** — Salesforce and HubSpot have deep Gmail/Outlook integration (sidebar widgets, email logging, template insertion). Ripple spec mentions email but doesn't detail the integration architecture. How does email get into Ripple?

2. **Calendar integration** — HubSpot has a meeting scheduler link. Dynamics has full Outlook calendar sync. How does Ripple handle calendar sync and booking?

3. **Mobile app** — Salesforce and HubSpot have full mobile apps. Dynamics has Power Apps mobile. Ripple spec doesn't mention mobile. For field sales, this is critical.

4. **Telephony/VoIP** — HubSpot has built-in calling. Salesforce integrates with RingCentral, Dialpad. What's Ripple's telephony strategy?

5. **Marketing automation connection** — Salesforce has Marketing Cloud/Pardot. HubSpot has Marketing Hub. Dynamics has Customer Insights - Journeys. Ripple has Spark (the Three Marketing Brains) but the integration between Spark and Ripple isn't detailed.

6. **Workflow automation** — Salesforce has Flow Builder. HubSpot has Workflows. Dynamics has Power Automate. What's Ripple's automation engine? (ELAINE + n8n?)

7. **Customer portal/community** — Salesforce has Experience Cloud. HubSpot has customer portal. Does Ripple need one?

8. **Document management** — Salesforce has Files. HubSpot has document tracking (know when someone views your proposal). Dynamics has SharePoint integration. Ripple has proposal generation but no document tracking/analytics.

9. **Conversational intelligence** — Gong, Chorus, and now Einstein Conversation Insights in Salesforce. HubSpot has Conversation Intelligence. Ripple's Meeting Intelligence Hub could include this with transcript analysis.

10. **Revenue intelligence** — Clari-style features are being absorbed into CRMs. Pipeline inspection, deal health scoring, forecast accuracy tracking. Ripple has some of this but could go deeper.

---

## 4. RECOMMENDED PROMPT FOR LLM FEEDBACK

Give other LLMs the Ripple v3 spec along with this covering note:

> *"I'm building Ripple, a Relationship Intelligence CRM for Australian and New Zealand SMBs (5-200 employees). Attached is the v3 product specification. Please review it against the current feature sets of: Salesforce Sales Cloud (Enterprise), HubSpot Sales Hub (Professional), Microsoft Dynamics 365 Sales (Premium), Zoho CRM (Enterprise), and Pipedrive (Professional).*
>
> *For each of these areas, tell me: (1) What are table-stakes features in 2026 that Ripple is missing? (2) What are emerging features the leaders are shipping that Ripple should consider? (3) Where does Ripple genuinely differentiate?*
>
> *Areas to review: Contact Management, Company/Account Management, Lead Management, Pipeline/Deal Management, Sales Sequences, Email & Calendar Integration, Telephony, Mobile App, Reporting & Dashboards, AI/ML Features, Territory Management, Forecasting, CPQ/Quoting, Document Management, Workflow Automation, Meeting Intelligence, Customer Portal, API & Integrations, Data Privacy/GDPR Compliance, Onboarding & User Adoption.*
>
> *Be brutally honest. I'd rather know now what's missing than discover it when customers compare us to Salesforce."*

---

*Thalaiva — 12 February 2026*

# Ripple CRM — Integration Notes

## AMTL Ecosystem Connections (Phase 2+)

### Matomo Analytics (Port 8084)
- Matomo tracking snippet added to `frontend/index.html`
- Site ID: 1
- Tracks page views, link clicks across Ripple CRM frontend
- Full dashboard at http://localhost:8084

### Touchstone Attribution (Port 8200)
- CRM webhooks: Ripple can push deal events to Touchstone `/api/v1/webhooks/crm`
- Contact sync: Touchstone identifies contacts by email — same as Ripple
- Future: Automatic attribution when contacts convert to customers in Ripple

### KnowYourself (Port 8300)
- Personality profiles could enrich contact records (Phase 3+)
- Big Five scores may inform communication style recommendations
- Journal themes could correlate with deal outcomes

### ELAINE (Port 5000)
- ELAINE's tool registry includes Ripple CRM at http://localhost:8100
- `/api/tools/health` pings Ripple's health endpoint
- Future: "ELAINE, show me my top contacts" via Ripple API

### Ollama / Supervisor (Port 9000 / 11434)
- Ripple Phase 2 deferred: Ollama integration for contact insights
- Channel DNA service already integrates Supervisor-first routing
- Model: gemma2:27b for text analysis

### Wisdom Quotes (Port 3350)
- Available via ELAINE `/api/wisdom` endpoint
- Could be shown in Ripple contact detail view as daily inspiration

## Connection Points for Future Phases
1. **Email/Calendar sync** — deferred until n8n workflows mature
2. **PDF export** — deferred, Swiss Army Knife already has PDF capability
3. **Trust Decay visualisation** — deferred, needs frontend chart component
4. **Ollama contact insights** — needs Supervisor routing, Phase 2.2

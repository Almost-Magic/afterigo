# AMTL_NEW_TOOLS_INSTALL.md
## Claude Code Instructions — New Open Source Tools
### Almost Magic Tech Lab — February 2026

---

## CRITICAL RULES — SAME AS WSL2_TOOLKIT_INSTALL.md

1. **Ollama only for programmatic AI.** Route through Supervisor on port 9000. If Supervisor isn't available, fall back to Ollama direct on 11434.
2. **NO cloud API keys. EVER.** Not in .env, not in docker-compose, not anywhere.
3. **You're working in WSL2 — use Linux commands, not PowerShell.**
4. **Use `MSYS_NO_PATHCONV=1` when passing Linux paths from Git Bash to WSL.**
5. **Test each tool after installing.** Don't batch-install and hope.
6. **Log what you installed** in the STATUS section at the bottom.
7. **Docker containers run on Windows Docker Desktop** — they're accessible from both Windows and WSL2.

---

## EXISTING INFRASTRUCTURE (Do NOT reinstall)

| Service | Port | Notes |
|---------|------|-------|
| Genie Frontend | 3000 | |
| Uptime Kuma | 3001 | |
| Outline | 3006 | |
| LangFuse | 3007 | |
| PostgreSQL (pgvector) | 5433 | Password: peterman2026 |
| Redis | 6379 | |
| n8n | 5678 | |
| SearXNG | 8888 | |
| Genie Backend | 8000 | |
| Listmonk | 9001 | |
| Supervisor | 9000 | |
| Ollama | 11434 | OLLAMA_HOST=0.0.0.0:11434 on Windows |
| MailPit SMTP | 1025 | |
| MailPit Web | 8025 | |
| OpenVAS/Greenbone | 9392 | |
| Wazuh Dashboard | 4443 | |
| Wazuh Indexer | 9200 | |
| Netdata | 19999 | In WSL2 |
| SpiderFoot | 5009 | |

---

## TOOL 1: Paperless-ngx (Document Management + OCR)

### What it does
Scans, OCRs, auto-tags, and archives documents. Drop a PDF in a folder, it processes it automatically.

### Install

```bash
mkdir -p /tmp/paperless-ngx && cat > /tmp/paperless-ngx/docker-compose.yml << 'EOF'
version: "3.8"
services:
  paperless-broker:
    image: docker.io/library/redis:7
    container_name: paperless-redis
    restart: unless-stopped
    volumes:
      - paperless-redis-data:/data

  paperless-webserver:
    image: ghcr.io/paperless-ngx/paperless-ngx:latest
    container_name: paperless-ngx
    restart: unless-stopped
    depends_on:
      - paperless-broker
    ports:
      - "8010:8000"
    volumes:
      - paperless-data:/usr/src/paperless/data
      - paperless-media:/usr/src/paperless/media
      - paperless-export:/usr/src/paperless/export
      - paperless-consume:/usr/src/paperless/consume
    environment:
      PAPERLESS_REDIS: redis://paperless-broker:6379
      PAPERLESS_DBENGINE: sqlite
      PAPERLESS_OCR_LANGUAGE: eng
      PAPERLESS_OCR_MODE: skip
      PAPERLESS_ADMIN_USER: amtl-admin
      PAPERLESS_ADMIN_PASSWORD: AmtlPaperless2026!
      PAPERLESS_URL: http://localhost:8010
      PAPERLESS_TIME_ZONE: Australia/Sydney
      PAPERLESS_CONSUMER_POLLING: 30
      PAPERLESS_CONSUMER_RECURSIVE: "true"

volumes:
  paperless-redis-data:
  paperless-data:
  paperless-media:
  paperless-export:
  paperless-consume:
EOF

cd /tmp/paperless-ngx && docker compose up -d
```

NOTE: Using its own Redis instance (not port 6379) to avoid conflicts with existing Redis. The internal Redis is only accessible between paperless containers.

### Test
```bash
# Wait for startup (can take 60-90 seconds on first run)
sleep 90

# Health check
curl -s http://localhost:8010/api/ | head -20

# Login test — should return a token
curl -s -X POST http://localhost:8010/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"amtl-admin","password":"AmtlPaperless2026!"}' | jq .
```

**Expected:** API responds. Token returned. Login at http://localhost:8010 with amtl-admin / AmtlPaperless2026!

---

## TOOL 2: Perplexica (AI Search Engine)

### What it does
Self-hosted Perplexity alternative. Uses SearXNG (already on 8888) + Ollama for AI-powered search with citations.

### Install

Using the slim image since we already have SearXNG running.

```bash
docker run -d \
  --name perplexica \
  --restart=unless-stopped \
  -p 3008:3000 \
  -v perplexica-data:/home/perplexica/data \
  -e SEARXNG_API_URL=http://host.docker.internal:8888 \
  --add-host=host.docker.internal:host-gateway \
  itzcrazykns1337/perplexica:slim-latest
```

### Configure
After the container starts, open http://localhost:3008 in a browser. In Settings:
- **Chat Model Provider:** Ollama
- **Ollama API URL:** http://host.docker.internal:11434
- **Chat Model:** gemma2:27b (or whatever model is loaded in Ollama)
- **Embedding Model Provider:** Ollama
- **Embedding Model:** nomic-embed-text (pull this in Ollama first if not available)

If you can't access the settings UI, check if there's a config.toml inside the container and update it:
```bash
docker exec -it perplexica cat /home/perplexica/data/config.toml 2>/dev/null || echo "Config not found — use UI settings"
```

### Pre-requisite: Ensure Ollama has an embedding model
```bash
# From WSL2 or Windows terminal:
curl -s http://localhost:11434/api/tags | jq '.models[].name'

# If nomic-embed-text is not listed:
curl -X POST http://localhost:11434/api/pull -d '{"name": "nomic-embed-text"}'
```

### Test
```bash
# Container running check
docker ps | grep perplexica

# Web UI should respond
curl -s -o /dev/null -w "%{http_code}" http://localhost:3008
```

**Expected:** HTTP 200. Open http://localhost:3008 in browser, ask a question, get a cited AI answer.

---

## TOOL 3: Docling (Document Parser — Python library)

### What it does
Converts PDFs, DOCX, PPTX, XLSX, images into structured Markdown/JSON. Runs locally, MIT license.

### Install

Install into the existing paperai virtual environment (created in Phase 5 of the toolkit):

```bash
# If the paperai-env exists:
source ~/paperai-env/bin/activate 2>/dev/null

# If it doesn't exist, create it:
if [ ! -d ~/paperai-env ]; then
    python3 -m venv ~/paperai-env
    source ~/paperai-env/bin/activate
fi

# Install Docling
pip install docling

# Verify
python3 -c "from docling.document_converter import DocumentConverter; print('Docling: OK')"

deactivate
```

### Test
```bash
source ~/paperai-env/bin/activate

cat > /tmp/test-docling.py << 'PYEOF'
"""Docling test — convert a PDF to Markdown locally."""
from docling.document_converter import DocumentConverter

# Convert the Docling technical report from arXiv
source = "https://arxiv.org/pdf/2408.09869"
converter = DocumentConverter()
result = converter.convert(source)
md = result.document.export_to_markdown()
print(f"Converted {len(md)} characters of Markdown")
print(f"\nFirst 500 chars:\n{md[:500]}")
print("\n✅ Docling test PASSED")
PYEOF

python3 /tmp/test-docling.py
deactivate
```

NOTE: First run downloads models from HuggingFace (~500MB). This is a one-time download. If network access is restricted from WSL2, the test may fail — log this and move on. The library is still installed correctly.

**Expected:** PDF converted to structured Markdown with headers, tables, and layout preserved.

---

## TOOL 4: Karakeep (Bookmark Everything + AI Tagging)

### What it does
Save links, notes, images, PDFs with AI auto-tagging via Ollama. Full-text search. Browser extension.

### Install

```bash
mkdir -p /tmp/karakeep && cat > /tmp/karakeep/docker-compose.yml << 'EOF'
version: "3.8"
services:
  karakeep:
    image: ghcr.io/karakeep-app/karakeep:release
    container_name: karakeep
    restart: unless-stopped
    ports:
      - "3009:3000"
    volumes:
      - karakeep-data:/data
    environment:
      MEILI_ADDR: http://karakeep-meilisearch:7700
      BROWSER_WEB_URL: http://karakeep-chrome:9222
      DATA_DIR: /data
      NEXTAUTH_SECRET: amtl-karakeep-secret-2026
      NEXTAUTH_URL: http://localhost:3009
      # Ollama integration — no cloud APIs
      INFERENCE_TEXT_MODEL: ollama/gemma2
      INFERENCE_IMAGE_MODEL: ollama/llava
      OLLAMA_BASE_URL: http://host.docker.internal:11434
      DISABLE_SIGNUPS: "false"
    extra_hosts:
      - "host.docker.internal:host-gateway"

  karakeep-chrome:
    image: gcr.io/zenika-hub/alpine-chrome:124
    container_name: karakeep-chrome
    restart: unless-stopped
    command:
      - --no-sandbox
      - --disable-gpu
      - --disable-dev-shm-usage
      - --remote-debugging-address=0.0.0.0
      - --remote-debugging-port=9222
      - --hide-scrollbars

  karakeep-meilisearch:
    image: getmeili/meilisearch:v1.12
    container_name: karakeep-meilisearch
    restart: unless-stopped
    environment:
      MEILI_NO_ANALYTICS: "true"
    volumes:
      - karakeep-meilisearch-data:/meili_data

volumes:
  karakeep-data:
  karakeep-meilisearch-data:
EOF

cd /tmp/karakeep && docker compose up -d
```

NOTE: If the exact image tag or environment variables have changed, check https://docs.karakeep.app/installation/docker for the latest docker-compose. Adapt but keep the Ollama config pointing to host.docker.internal:11434.

### Test
```bash
# Wait for startup
sleep 30

# Health check
curl -s -o /dev/null -w "%{http_code}" http://localhost:3009

# Check containers
docker ps | grep karakeep
```

**Expected:** HTTP 200 at http://localhost:3009. Register first account (becomes admin). Save a test bookmark and verify AI auto-tagging appears.

---

## TOOL 5: Homepage (Service Dashboard)

### What it does
Beautiful dashboard showing all AMTL services with status, quick links, and Docker stats.

### Install

```bash
mkdir -p /tmp/homepage && cat > /tmp/homepage/docker-compose.yml << 'EOF'
version: "3.8"
services:
  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    restart: unless-stopped
    ports:
      - "3011:3000"
    volumes:
      - homepage-config:/app/config
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      PUID: 1000
      PGID: 1000

volumes:
  homepage-config:
EOF

cd /tmp/homepage && docker compose up -d
```

### Configure services

After the container starts, create the services config:

```bash
# Find the config volume mount path
HOMEPAGE_CONFIG=$(docker inspect homepage --format '{{ range .Mounts }}{{ if eq .Destination "/app/config" }}{{ .Source }}{{ end }}{{ end }}')

# Create services.yaml
cat > "${HOMEPAGE_CONFIG}/services.yaml" << 'YAML'
- AMTL Core:
    - Genie Frontend:
        href: http://localhost:3000
        description: Finance App
        icon: si-cashapp
    - Genie Backend:
        href: http://localhost:8000/api/health
        description: API Health
        icon: si-fastapi
    - The Workshop:
        href: http://localhost:5003
        description: App Registry
        icon: si-workshop
    - Supervisor:
        href: http://localhost:9000/api/health
        description: Process Manager
        icon: si-supervisor

- Knowledge & Search:
    - Outline Wiki:
        href: http://localhost:3006
        description: AMTL Intranet
        icon: si-outline
    - Perplexica:
        href: http://localhost:3008
        description: AI Search
        icon: si-perplexity
    - Karakeep:
        href: http://localhost:3009
        description: Bookmarks & Research
        icon: si-bookmark
    - SearXNG:
        href: http://localhost:8888
        description: Meta Search
        icon: si-searxng

- Monitoring & Observability:
    - Uptime Kuma:
        href: http://localhost:3001
        description: Service Monitoring
        icon: si-uptimekuma
    - LangFuse:
        href: http://localhost:3007
        description: LLM Observability
        icon: si-langchain
    - Netdata:
        href: http://localhost:19999
        description: System Metrics
        icon: si-netdata

- Documents & Email:
    - Paperless-ngx:
        href: http://localhost:8010
        description: Document Archive
        icon: si-paperlessngx
    - Listmonk:
        href: http://localhost:9001
        description: Email Campaigns
        icon: si-maildotru
    - MailPit:
        href: http://localhost:8025
        description: Dev Email Catcher
        icon: si-maildotru

- Security:
    - OpenVAS:
        href: http://127.0.0.1:9392
        description: Vulnerability Scanner
        icon: si-openvas
    - Wazuh:
        href: https://localhost:4443
        description: SIEM Dashboard
        icon: si-wazuh
    - SpiderFoot:
        href: http://localhost:5009
        description: OSINT Platform
        icon: si-spider

- Infrastructure:
    - n8n:
        href: http://localhost:5678
        description: Workflow Automation
        icon: si-n8n
    - Ollama:
        href: http://localhost:11434
        description: Local LLM Engine
        icon: si-ollama
    - PostgreSQL:
        description: pgvector on port 5433
        icon: si-postgresql
    - Redis:
        description: Cache on port 6379
        icon: si-redis
YAML

# Restart to pick up config
docker restart homepage
```

### Test
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3011
```

**Expected:** HTTP 200. Open http://localhost:3011 — see all AMTL services organised in categories with quick links.

---

## TOOL 6: Docuseal (Document Signing)

### What it does
Open-source DocuSign alternative. Create templates, send for e-signature, track completion.

### Install

```bash
docker run -d \
  --name docuseal \
  --restart=unless-stopped \
  -p 3010:3000 \
  -v docuseal-data:/data \
  docuseal/docuseal:latest
```

### Test
```bash
sleep 15
curl -s -o /dev/null -w "%{http_code}" http://localhost:3010
```

**Expected:** HTTP 200. Open http://localhost:3010, create admin account on first visit.

---

## TOOL 7: Memos (Quick Note Capture)

### What it does
Lightweight, Twitter-style self-hosted notes. Quick capture of thoughts, snippets, commands.

### Install

```bash
docker run -d \
  --name memos \
  --restart=unless-stopped \
  -p 5230:5230 \
  -v memos-data:/var/opt/memos \
  neosmemo/memos:stable
```

### Test
```bash
sleep 10
curl -s -o /dev/null -w "%{http_code}" http://localhost:5230
```

**Expected:** HTTP 200. Open http://localhost:5230, create first account (becomes admin).

---

## POST-INSTALL: Add monitors to Uptime Kuma

After all tools are installed, add monitors for each new service in Uptime Kuma (http://localhost:3001):

| Name | Type | URL/Host | Port |
|------|------|----------|------|
| Paperless-ngx | HTTP | http://localhost:8010 | 8010 |
| Perplexica | HTTP | http://localhost:3008 | 3008 |
| Karakeep | HTTP | http://localhost:3009 | 3009 |
| Homepage | HTTP | http://localhost:3011 | 3011 |
| Docuseal | HTTP | http://localhost:3010 | 3010 |
| Memos | HTTP | http://localhost:5230 | 5230 |

Use the Uptime Kuma API or add manually via the web UI.

---

## UPDATED PORT MAP (After install)

| Port | Service | Status |
|------|---------|--------|
| 1025 | MailPit SMTP | Existing |
| 3000 | Genie Frontend | Existing |
| 3001 | Uptime Kuma | Existing |
| 3006 | Outline | Existing |
| 3007 | LangFuse | Existing |
| 3008 | Perplexica | **NEW** |
| 3009 | Karakeep | **NEW** |
| 3010 | Docuseal | **NEW** |
| 3011 | Homepage | **NEW** |
| 4443 | Wazuh Dashboard | Existing |
| 5003 | The Workshop | Existing |
| 5009 | SpiderFoot | Existing |
| 5230 | Memos | **NEW** |
| 5433 | PostgreSQL | Existing |
| 5678 | n8n | Existing |
| 6379 | Redis | Existing |
| 8000 | Genie Backend | Existing |
| 8010 | Paperless-ngx | **NEW** |
| 8025 | MailPit Web | Existing |
| 8888 | SearXNG | Existing |
| 9000 | Supervisor | Existing |
| 9001 | Listmonk | Existing |
| 9200 | Wazuh Indexer | Existing |
| 9392 | OpenVAS | Existing |
| 11434 | Ollama | Existing |
| 19999 | Netdata | Existing |
| 3333 | Ghostfolio | **NEW** |
| 9050 | Tor SOCKS5 Proxy | **OSINT** |
| 8118 | Privoxy HTTP Proxy | **OSINT** |
| 8282 | IVRE Network Recon | **OSINT** |
| 8284 | HIBP Offline Checker | **OSINT** |

---

## STATUS LOG

| Tool | Status | Date | Notes |
|------|--------|------|-------|
| Paperless-ngx | INSTALLED | 2026-02-13 | Port 8010, HTTP 302 (auth redirect), token API working, admin: amtl-admin / AmtlPaperless2026! |
| Perplexica | INSTALLED | 2026-02-13 | Port 3008, HTTP 200, slim image using existing SearXNG:8888. Configure Ollama via UI settings. |
| Docling | INSTALLED | 2026-02-13 | Python lib in ~/paperai-env (WSL2). `from docling.document_converter import DocumentConverter` verified OK. |
| Karakeep | INSTALLED | 2026-02-13 | Port 3009, HTTP 307 (auth redirect), healthy. Ollama at host.docker.internal:11434 for AI tagging. |
| Homepage | INSTALLED | 2026-02-13 | Port 3011, HTTP 200, services.yaml configured with 6 categories, 20+ services. |
| Docuseal | INSTALLED | 2026-02-13 | Port 3010, HTTP 302 (setup redirect). Create admin account on first visit. |
| Memos | INSTALLED | 2026-02-13 | Port 5230, HTTP 200. Create first account (becomes admin). |
| Uptime Kuma monitors | MANUAL | 2026-02-13 | Uptime Kuma uses WebSocket API — add 6 monitors via web UI at http://localhost:3001 |
| FinceptTerminal Desktop | INSTALLED | 2026-02-13 | v3.3.0 at C:\Program Files\FinceptTerminal\. Desktop shortcut + Start Menu. Tauri app. |
| FinceptTerminal CLI | INSTALLED | 2026-02-13 | v2.0.8 in ~/fincept-env (WSL2). `source ~/fincept-env/bin/activate && fincept` |
| OpenBB | INSTALLED | 2026-02-13 | v4.6.0 in ~/fincept-env (WSL2). 30+ provider extensions. Free data: yfinance, FRED, SEC, OECD. |
| Ghostfolio | INSTALLED | 2026-02-13 | Port 3333, 3 containers (ghostfolio, gf-postgres, gf-redis). Health: OK. Create admin on first visit. |
| Homepage update | DONE | 2026-02-13 | Added "Market Intelligence" category with FinceptTerminal, Ghostfolio, OpenBB. |
| Workshop update | DONE | 2026-02-13 | Added FinceptTerminal + Ghostfolio cards in CK section, backend SERVICES dict updated. |
| Tor SOCKS5 Proxy | INSTALLED | 2026-02-13 | Port 9050. peterdavehello/tor-socks-proxy. IsTor:true verified. Anonymous SOCKS5 routing for all OSINT tools. |
| Privoxy HTTP Proxy | INSTALLED | 2026-02-13 | Port 8118. vimagick/privoxy. Converts SOCKS5 to HTTP proxy. Forwards through Tor. |
| IVRE Network Recon | INSTALLED | 2026-02-13 | Port 8282. Self-hosted Shodan alternative. 5 containers (web, uwsgi, doku, MongoDB, client). HTTP 200. |
| HIBP Offline Checker | INSTALLED | 2026-02-13 | Port 8284. Custom Flask app. Placeholder until 35GB hash DB downloaded. 3 endpoints: check-password, check-hash, health. |
| SpiderFoot Tor routing | CONFIGURED | 2026-02-13 | Connected to osint-net Docker network. tor-socks-proxy reachable. Must set SOCKS5 proxy in web UI (http://localhost:5009 > Settings). |
| Homepage OSINT | DONE | 2026-02-13 | Added "Security & OSINT" category with all new tools. |
| Workshop OSINT | DONE | 2026-02-13 | Added 4 OSINT tool cards (Tor, Privoxy, IVRE, HIBP) to OSS grid. |
| DARKWEB_OSINT_INTEGRATION.md | CREATED | 2026-02-13 | Full documentation: Tor routing, Ahmia API, SpiderFoot config, Identity Atlas integration, ethical guidelines. |

---

*Made with ❤️ by Mani Padisetti @ Almost Magic Tech Lab*

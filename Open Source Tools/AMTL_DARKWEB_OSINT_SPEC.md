# AMTL Dark Web & OSINT Intelligence Layer

## Overview

This spec adds a **dark web intelligence layer** to AMTL's security toolkit. It provides anonymous searching, breach detection, and network reconnaissance — all self-hosted, no cloud API keys required.

The tools serve two primary use cases:
1. **Identity Atlas / KnowYourself** — check if a person's data has been exposed in breaches or is visible on the dark web
2. **SpiderFoot OSINT** — anonymous reconnaissance that can reach .onion sites and clearnet without revealing your IP

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AMTL OSINT Stack                          │
├──────────────┬──────────────┬───────────────┬───────────────┤
│  Tor Proxy   │   Privoxy    │     IVRE      │  HIBP Offline │
│  SOCKS5      │   HTTP Proxy │   Network     │  Breach Check │
│  :9050       │   :8118      │   Recon :8282 │  :8284        │
├──────────────┴──────┬───────┴───────────────┴───────────────┤
│                     │                                        │
│   SpiderFoot (:5009)│   Identity Atlas (future)              │
│   routes through    │   routes through                       │
│   Tor for anonymous │   HIBP offline for                     │
│   OSINT scanning    │   breach detection                     │
└─────────────────────┴────────────────────────────────────────┘
```

---

## Tools to Install

### Tier 1 — Core Infrastructure (this command)

| Tool | Port | Purpose | Docker Image |
|------|------|---------|-------------|
| **Tor SOCKS5 Proxy** | 9050 | Anonymous network routing, .onion access | `peterdavehello/tor-socks-proxy` |
| **Privoxy** | 8118 | HTTP proxy (converts SOCKS→HTTP for tools that don't support SOCKS) | `vimagick/privoxy` |
| **IVRE** | 8282 | Self-hosted Shodan alternative — network recon, passive DNS, scan results browser | `ivre/web` + `ivre/db` |
| **HIBP Offline Checker** | 8284 | Offline breach/password check using downloaded HIBP hash database | Custom Python + HIBP data |

### Tier 2 — API Services (free tiers, add API keys later)

| Service | What It Does | Free Tier | Integration Point |
|---------|-------------|-----------|-------------------|
| **Shodan** (shodan.io) | Internet-connected device search, port scanning, vulnerability detection | Free: 100 queries/month, limited filters | SpiderFoot module, IVRE enrichment |
| **Have I Been Pwned** (haveibeenpwned.com) | Email/password breach checking against 14B+ records | Free: manual search. API: $3.50/month (HIBP-RP key) | Identity Atlas, KnowYourself |
| **Ahmia.fi** | .onion search engine with API | Free, unlimited | Dark web search in Identity Atlas |
| **IntelX** (intelx.io) | Intelligence search across dark web, paste sites, data leaks | Free: 10 searches/day | SpiderFoot module |
| **Censys** (search.censys.io) | Internet asset discovery, certificate transparency | Free: 250 queries/month | SpiderFoot module |

### Decision: Shodan vs IVRE vs Both

**IVRE** is the self-hosted Shodan alternative. It's free, unlimited, and you own the data. But it only scans networks YOU point it at — it doesn't have Shodan's pre-built database of the entire internet.

**Shodan** has already scanned the entire internet. Its free tier gives you 100 searches/month which is plenty for occasional lookups.

**Recommendation: Install IVRE now (free, self-hosted), add Shodan API key later when needed.** They complement each other — IVRE for your own network scanning, Shodan for looking up external targets.

### Decision: HIBP API vs Offline

**Have I Been Pwned API** costs $3.50/month but gives real-time breach data across 14B+ accounts.

**HIBP Offline** — you can download the SHA-1 password hash database (free, ~35GB) and check passwords locally. No API needed for password checking. Email breach checking still needs the API.

**Recommendation: Start with offline password hash check (free). Add HIBP API key ($3.50/month) later for email breach lookups.** Both integrate into Identity Atlas.

---

## Claude Code Command

Open a **new terminal window**. Confirm `/status` shows Guru (manip@almostmagic) Max subscription. Then navigate to the Source and Brand directory and paste:

```
claude "Install the AMTL Dark Web & OSINT intelligence layer in Docker via WSL2. Use wsl -d Ubuntu-24.04 -u amtl -- bash for all commands. Use MSYS_NO_PATHCONV=1 when passing paths.

IMPORTANT: Read CLAUDE.md first. Check existing Docker containers to avoid port conflicts.

## 1. Tor SOCKS5 Proxy (port 9050)

docker run -d \
  --name tor-socks-proxy \
  --restart=unless-stopped \
  -p 9050:9150/tcp \
  peterdavehello/tor-socks-proxy:latest

Test it works:
  docker exec tor-socks-proxy curl --socks5 localhost:9150 --socks5-hostname localhost:9150 -s https://check.torproject.org/api/ip
Should return: {\"IsTor\":true, ...}

## 2. Privoxy HTTP Proxy (port 8118)

Create a Privoxy config that forwards to Tor:
  forward-socks5t / 127.0.0.1:9050 .

docker run -d \
  --name privoxy \
  --restart=unless-stopped \
  --link tor-socks-proxy:tor \
  -p 8118:8118 \
  vimagick/privoxy

If vimagick/privoxy doesn't work or link doesn't resolve, use dperson/torproxy instead which bundles both:
  docker run -d --name tor-privoxy --restart=unless-stopped -p 8118:8118 -p 9050:9050 dperson/torproxy

Test HTTP proxy:
  curl -x http://localhost:8118 https://check.torproject.org/api/ip
Should also return IsTor: true.

## 3. IVRE — Self-hosted Network Recon (port 8282)

IVRE is a self-hosted alternative to Shodan. It uses Nmap, Masscan, and Zeek for scanning, with a web UI to browse results.

Clone the IVRE Docker setup:
  cd /tmp && git clone https://github.com/ivre/ivre.git ivre-src
  cd ivre-src/docker

Check their docker-compose.yml. The default web UI port is 80 — change it to 8282.
  docker compose up -d

If the full IVRE stack is too heavy (it uses MongoDB + multiple containers), install a lightweight version:
  docker run -d --name ivre-web --restart=unless-stopped -p 8282:80 ivre/web

Test: curl -s -o /dev/null -w '%{http_code}' http://localhost:8282
Should return 200 or 302.

## 4. HIBP Offline Password Checker (port 8284)

This is a lightweight Python API that checks passwords against the HIBP SHA-1 hash database.

Create the checker in WSL2:

mkdir -p ~/hibp-checker && cd ~/hibp-checker

Create a Python Flask app (app.py) that:
- Accepts POST /api/check-password with {\"password\": \"...\"} body
- Hashes password with SHA-1
- Returns {\"breached\": false, \"count\": 0} if not found, or {\"breached\": true, \"count\": N} if found
- Also accepts POST /api/check-hash with {\"hash\": \"...\"} for pre-hashed lookups
- Has GET /api/health returning {\"status\": \"ok\", \"service\": \"hibp-offline\"}
- NOTE: The full HIBP hash database is 35GB. For now, create the API structure with a placeholder that returns {\"breached\": false, \"note\": \"Full HIBP database not yet downloaded. Run download-hibp.sh to fetch.\"}
- Create a download-hibp.sh script that documents how to download the full hash database from https://haveibeenpwned.com/Passwords (using the torrent or API download)
- Run on port 8284 in a Docker container

Build and run:
  docker build -t hibp-checker .
  docker run -d --name hibp-checker --restart=unless-stopped -p 8284:8284 hibp-checker

## 5. Wire SpiderFoot to use Tor proxy

SpiderFoot is already running on port 5009. Update its configuration to use the Tor SOCKS proxy:
- Check SpiderFoot's Docker container for config files
- Set SOCKS proxy to localhost:9050 or the Docker network equivalent
- If SpiderFoot can't be configured via file, note that it can be configured via the web UI at http://localhost:5009 under Settings > Global > SOCKS Proxy

## 6. Registration

A. Update Homepage (port 3011) services.yaml — add all new tools under a 'Security & OSINT' category with appropriate icons and descriptions. docker cp the updated file and restart.

B. Update Workshop (port 5003) — add Tor Proxy, IVRE, and HIBP Checker cards to the CK section. Update the SERVICES dict in app.py and add cards to templates/index.html.

C. Add Uptime Kuma (port 3001) HTTP monitors:
   - Tor SOCKS proxy: TCP monitor on port 9050
   - Privoxy: HTTP monitor on http://localhost:8118 (will fail without proxy target, use TCP on 8118)
   - IVRE: HTTP monitor on http://localhost:8282
   - HIBP Checker: HTTP monitor on http://localhost:8284/api/health

D. Update WSL2_TOOLKIT_INSTALL.md with ports and status.

E. Update AMTL_NEW_TOOLS_INSTALL.md with installation status.

F. Create DARKWEB_OSINT_INTEGRATION.md documenting:
   - All tools installed, ports, login URLs
   - How to route any Python script through Tor (requests + PySocks example)
   - How to search .onion sites via Ahmia API
   - How SpiderFoot uses the Tor proxy
   - Future integration points with Identity Atlas and KnowYourself
   - How to add Shodan/HIBP/Censys API keys later
   - Security notes: what's legal, ethical OSINT guidelines

G. Commit everything with message: 'OSINT layer: Tor proxy, Privoxy, IVRE, HIBP offline checker, SpiderFoot dark web routing'

H. Push to origin main.

Don't ask me anything. Work around problems and log what you did. If a tool fails, skip it, log the error, and continue. Australian English in all docs."
```

---

## What Each Tool Does (Plain English)

### Tor SOCKS5 Proxy (port 9050)
**What:** An anonymous network tunnel. Any tool can route its traffic through this to hide your IP address and access .onion (dark web) sites.
**Why:** SpiderFoot OSINT scans reveal your IP to targets. Tor hides it. Also lets you access .onion sites programmatically.
**Size:** ~10MB Docker image. Minimal resources.

### Privoxy (port 8118)
**What:** Converts the SOCKS5 proxy into an HTTP proxy. Some tools only speak HTTP proxying, not SOCKS.
**Why:** Bridges the gap for tools that can't use SOCKS directly. Also adds ad/tracker blocking.
**Size:** ~5MB Docker image.

### IVRE (port 8282) — Your Self-Hosted Shodan
**What:** Network reconnaissance framework with a web UI. You point it at networks and it scans them using Nmap/Masscan, then lets you browse and search results like Shodan.
**Why:** Shodan has scanned the entire internet but costs money. IVRE lets you scan YOUR targets for free, unlimited, with full control. Use Shodan's free tier (100/month) for quick external lookups, IVRE for deep dives.
**Size:** ~500MB with MongoDB backend.

### HIBP Offline Checker (port 8284)
**What:** Checks passwords against the Have I Been Pwned database locally. No API calls, no fees.
**Why:** Identity Atlas and KnowYourself can check if a user's passwords have appeared in known breaches — entirely offline and private.
**Size:** API is tiny. Full hash database is ~35GB (downloaded separately when needed).

---

## Integration Points

### Identity Atlas (future)
```python
# Check if an email has been breached (requires HIBP API key later)
import requests
headers = {"hibp-api-key": "YOUR_KEY"}
r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", headers=headers)

# Check if a password has been compromised (local, free)
r = requests.post("http://localhost:8284/api/check-password", json={"password": "test123"})
# Returns: {"breached": true, "count": 86495}
```

### SpiderFoot
```python
# SpiderFoot automatically routes through Tor when configured
# Settings > Global > SOCKS Proxy > 127.0.0.1:9050
# This anonymises ALL SpiderFoot scans
```

### Any Python Script via Tor
```python
import requests

# Route through Tor SOCKS5
proxies = {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}
r = requests.get("http://some-onion-site.onion", proxies=proxies)

# Route through Privoxy HTTP proxy
proxies = {"http": "http://localhost:8118", "https": "http://localhost:8118"}
r = requests.get("https://ahmia.fi/api/search?q=example", proxies=proxies)
```

### Ahmia Dark Web Search (free, no API key)
```python
# Search .onion sites via Ahmia's API
r = requests.get("https://ahmia.fi/api/search", params={"q": "data breach"}, proxies=proxies)
results = r.json()  # Returns list of .onion sites matching the query
```

---

## Port Summary

| Port | Service | Type | Status |
|------|---------|------|--------|
| 9050 | Tor SOCKS5 Proxy | Docker | NEW |
| 8118 | Privoxy HTTP Proxy | Docker | NEW |
| 8282 | IVRE Web UI | Docker | NEW |
| 8284 | HIBP Offline Checker | Docker | NEW |
| 5009 | SpiderFoot (existing) | Docker | UPDATE config |

---

## Future API Keys (add when needed)

| Service | Cost | What You Get | Where to Sign Up |
|---------|------|-------------|-----------------|
| Shodan | Free (100/month) | Search internet-connected devices globally | https://account.shodan.io/register |
| HIBP API | $3.50/month | Real-time email breach checking (14B+ records) | https://haveibeenpwned.com/API/Key |
| Censys | Free (250/month) | Certificate transparency, internet asset search | https://search.censys.io/register |
| IntelX | Free (10/day) | Dark web, paste sites, data leak search | https://intelx.io/signup |
| VirusTotal | Free (500/day) | File/URL/IP malware analysis | https://www.virustotal.com/gui/join-us |

None of these are required for the initial install. Everything works self-hosted and free. Add API keys later through SpiderFoot's web UI (Settings > Modules) or through environment variables.

---

## Ethical & Legal Notes

All tools installed here are for **defensive security and legitimate OSINT**:

- **Breach checking:** Verify if YOUR or YOUR CLIENT'S credentials have been exposed
- **Anonymous scanning:** Protect your identity during authorised security assessments
- **Dark web monitoring:** Check if client data has been leaked to dark web marketplaces
- **Network recon:** Scan networks YOU own or have written authorisation to test

Australian law (Criminal Code Act 1995, Part 10.7) prohibits unauthorised access to computer systems. Always ensure you have proper authorisation before scanning any network or system you don't own.

---

## Roadmap

**v1 (this install):** Tor proxy, Privoxy, IVRE, HIBP offline, SpiderFoot integration
**v2 (after Identity Atlas):** Wire breach checking into Identity Atlas risk score
**v3 (after KnowYourself):** Dark web exposure scan as part of KnowYourself security module
**v4 (API enrichment):** Add Shodan + HIBP + Censys API keys for deeper intelligence
**v5 (automated monitoring):** n8n workflow — daily dark web scan for client domains, alert on new breaches

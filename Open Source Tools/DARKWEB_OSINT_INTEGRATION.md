# DARKWEB_OSINT_INTEGRATION.md
## Almost Magic Tech Lab — Dark Web & OSINT Intelligence Layer
### Date: 13 February 2026

---

## Overview

The AMTL OSINT layer provides anonymous searching, breach detection, and network reconnaissance — entirely self-hosted, no cloud API keys required.

**Use cases:**
1. **Identity Atlas / KnowYourself** — check if a person's data has been exposed in breaches or is visible on the dark web
2. **SpiderFoot OSINT** — anonymous reconnaissance that can reach .onion sites and clearnet without revealing your IP
3. **Network recon** — self-hosted alternative to Shodan for scanning networks you own or have authorisation to test

---

## Installed Tools

| Tool | Port | Container(s) | Status |
|------|------|--------------|--------|
| **Tor SOCKS5 Proxy** | 9050 | `tor-socks-proxy` | Running |
| **Privoxy HTTP Proxy** | 8118 | `privoxy` | Running |
| **IVRE** (Network Recon) | 8282 | `ivreweb`, `ivreuwsgi`, `ivredb`, `ivredoku`, `ivreclient` | Running |
| **HIBP Offline Checker** | 8284 | `hibp-checker` | Running (placeholder — 35GB DB not downloaded) |
| **SpiderFoot** (existing) | 5009 | `spiderfoot` | Running, connected to `osint-net` Docker network |

---

## Architecture

```
+--------------------------------------------------------------+
|                    AMTL OSINT Stack                            |
+---------------+---------------+---------------+---------------+
|  Tor Proxy    |   Privoxy     |     IVRE      |  HIBP Offline |
|  SOCKS5       |   HTTP Proxy  |   Network     |  Breach Check |
|  :9050        |   :8118       |   Recon :8282 |  :8284        |
+-------+-------+-------+-------+---------------+---------------+
        |               |
  SpiderFoot (:5009)   Any Python script
  routes through       routes through
  Tor for anonymous    Tor for anonymous
  OSINT scanning       web access
+--------------------------------------------------------------+
```

---

## Quick Start

### Test Tor is working

```bash
# From WSL2
curl --socks5-hostname localhost:9050 https://check.torproject.org/api/ip
# Returns: {"IsTor":true,"IP":"..."}
```

### Test Privoxy (HTTP proxy via Tor)

```bash
curl -x http://localhost:8118 https://check.torproject.org/api/ip
# Returns: {"IsTor":true,"IP":"..."}
```

### Test IVRE

Open http://localhost:8282 in your browser. The web UI allows browsing scan results. To populate it, run scans from the `ivreclient` container.

### Test HIBP Checker

```bash
# Health check
curl http://localhost:8284/api/health

# Check a password (returns hash + breach status)
curl -X POST http://localhost:8284/api/check-password \
  -H "Content-Type: application/json" \
  -d '{"password":"test123"}'

# Check a pre-hashed value
curl -X POST http://localhost:8284/api/check-hash \
  -H "Content-Type: application/json" \
  -d '{"hash":"A94A8FE5CCB19BA61C4C0873D391E987982FBBD3"}'
```

**Note:** The HIBP checker returns placeholder responses until the full 35GB hash database is downloaded. Run `download-hibp.sh` (in the `~/hibp-checker/` directory on WSL2) for instructions.

---

## Routing Python Scripts Through Tor

### Via SOCKS5 (recommended)

```python
import requests

# Route through Tor SOCKS5 proxy
# socks5h:// means DNS resolution also goes through Tor
proxies = {
    "http": "socks5h://localhost:9050",
    "https": "socks5h://localhost:9050"
}

# Access a clearnet site anonymously
r = requests.get("https://httpbin.org/ip", proxies=proxies)
print(r.json())  # Shows Tor exit node IP, not yours

# Access a .onion site
r = requests.get("http://some-onion-address.onion", proxies=proxies)
```

**Requires:** `pip install requests[socks]` or `pip install PySocks`

### Via Privoxy HTTP Proxy

```python
import requests

# Route through Privoxy (which forwards to Tor)
# Useful for tools that only support HTTP proxies
proxies = {
    "http": "http://localhost:8118",
    "https": "http://localhost:8118"
}

r = requests.get("https://httpbin.org/ip", proxies=proxies)
print(r.json())  # Shows Tor exit node IP
```

### From Docker Containers

If your code runs in a Docker container, use the `osint-net` network:

```python
# Inside a container on osint-net:
proxies = {
    "http": "socks5h://tor-socks-proxy:9150",
    "https": "socks5h://tor-socks-proxy:9150"
}
```

---

## Ahmia Dark Web Search API

[Ahmia.fi](https://ahmia.fi) is a search engine for .onion sites. It has a free API with no authentication required.

```python
import requests

# Search .onion sites via Ahmia (clearnet API — no proxy needed for the search itself)
r = requests.get("https://ahmia.fi/api/search", params={"q": "data breach"})
results = r.json()

# Each result contains:
# - title: page title
# - url: .onion URL
# - description: snippet
for item in results.get("results", []):
    print(f"{item['title']}: {item['url']}")

# To actually visit a .onion result, route through Tor:
proxies = {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}
for item in results.get("results", [])[:3]:
    try:
        page = requests.get(item["url"], proxies=proxies, timeout=30)
        print(f"Fetched {item['url']}: {len(page.text)} bytes")
    except Exception as e:
        print(f"Failed {item['url']}: {e}")
```

---

## SpiderFoot Tor Integration

SpiderFoot (http://localhost:5009) has been connected to the Tor proxy via Docker networking.

### Configuration Steps (Web UI)

1. Open http://localhost:5009
2. Click **Settings** (top menu)
3. Under **Global** settings, set:
   - `_socks5proxy`: `tor-socks-proxy`
   - `_socks5port`: `9150`
4. Click **Save**
5. All subsequent SpiderFoot scans will route through Tor

### Docker Network

SpiderFoot and the Tor proxy are both on the `osint-net` Docker network. SpiderFoot resolves `tor-socks-proxy` by container name.

### What This Enables

- **Anonymous OSINT scanning** — your IP is hidden from scan targets
- **Dark web module** — SpiderFoot can access .onion sites for breach data
- **Passive reconnaissance** — DNS, WHOIS, and certificate lookups through Tor
- **Reduced fingerprinting** — scans appear to come from Tor exit nodes, not your IP

---

## IVRE Network Reconnaissance

IVRE (http://localhost:8282) is a self-hosted Shodan alternative. It uses Nmap, Masscan, and Zeek for scanning, with a web UI to browse results.

### Running a Scan

```bash
# Access the IVRE client container
docker exec -it ivreclient bash

# Initialise the database (first time only)
ivre ipinfo --init
ivre scancli --init
ivre view --init

# Run an Nmap scan (against your OWN network only)
nmap -sV -oX /ivre-share/scan-results.xml 192.168.4.0/24

# Import results into IVRE
ivre scan2db /ivre-share/scan-results.xml
ivre db2view nmap
```

Then browse results at http://localhost:8282.

### IVRE vs Shodan

| Feature | IVRE | Shodan |
|---------|------|--------|
| Cost | Free, self-hosted | Free: 100/month, paid for more |
| Data source | Scans you run | Pre-scanned internet |
| Coverage | Your targets only | Entire internet |
| Privacy | Fully private | Your searches logged |
| Best for | Deep dives on specific targets | Quick lookups of external hosts |

**Recommendation:** Use IVRE for your own network scanning, Shodan (free tier) for looking up external targets.

---

## Future API Keys (Add When Needed)

These are optional enrichment services. Everything works without them.

| Service | Cost | What It Adds | How to Configure |
|---------|------|-------------|-----------------|
| **Shodan** | Free (100/month) | Global device/port search | SpiderFoot > Settings > Modules > sfp_shodan > API key |
| **HIBP API** | $3.50/month | Real-time email breach checking (14B+ records) | Set `HIBP_API_KEY` env var for Identity Atlas |
| **Censys** | Free (250/month) | Certificate transparency, asset discovery | SpiderFoot > Settings > Modules > sfp_censys > API key |
| **IntelX** | Free (10/day) | Dark web, paste sites, leak search | SpiderFoot > Settings > Modules > sfp_inteltx > API key |
| **VirusTotal** | Free (500/day) | File/URL/IP malware analysis | SpiderFoot > Settings > Modules > sfp_virustotal > API key |

### Adding Shodan API Key

1. Register at https://account.shodan.io/register
2. Copy your API key from the account page
3. In SpiderFoot (http://localhost:5009):
   - Settings > Modules > `sfp_shodan`
   - Paste API key
   - Save

### Adding HIBP API Key

1. Purchase at https://haveibeenpwned.com/API/Key ($3.50/month)
2. For the HIBP offline checker, the API key is not needed (it uses the downloaded hash database)
3. For email breach lookups in Identity Atlas (future), set the key as an environment variable

### Adding Censys API Key

1. Register at https://search.censys.io/register
2. Go to Account > API to get your API ID and Secret
3. Configure in SpiderFoot under the `sfp_censys` module

---

## Future Integration Points

### Identity Atlas (Planned)

Identity Atlas will use the OSINT layer for:
- **Breach detection** — check client emails against HIBP API
- **Password audit** — check password hashes against HIBP offline database
- **Dark web monitoring** — search Ahmia for mentions of client domains
- **OSINT profile** — aggregate SpiderFoot findings into a risk score

### KnowYourself Security Module (Planned)

The KnowYourself tool will offer individuals:
- "Has my email been in a breach?" (HIBP API)
- "Is my password compromised?" (HIBP offline — completely private)
- "Is my data on the dark web?" (Ahmia search + SpiderFoot scan)

### n8n Automated Monitoring (Planned)

Weekly automated workflow:
1. Check client domain list against Ahmia dark web search
2. Check client email list against HIBP API
3. Run SpiderFoot passive scan on client IPs
4. Aggregate results into a weekly security digest
5. Send via Listmonk email campaign

---

## HIBP Database Download

The full HIBP password hash database is ~35GB. It is not included in the initial install.

### Download Instructions

SSH into WSL2 and run:

```bash
cd ~/hibp-checker
./download-hibp.sh
```

This script documents three download methods:
1. **Direct download** from haveibeenpwned.com/Passwords
2. **PwnedPasswordsDownloader** .NET tool (recommended)
3. **Torrent** (fastest for the 35GB file)

After downloading, restart the container:

```bash
docker restart hibp-checker
```

The API will automatically detect the database file at `/data/pwned-passwords-sha1-ordered-by-hash.txt` and switch from placeholder responses to real lookups using binary search.

---

## Docker Network Topology

```
osint-net (bridge)
  |-- tor-socks-proxy (192.168.16.x)
  |-- privoxy (192.168.16.x)
  |-- spiderfoot (192.168.16.x)

Default bridge
  |-- tor-socks-proxy
  |-- privoxy
  |-- hibp-checker

docker_default (IVRE compose)
  |-- ivreweb
  |-- ivreuwsgi
  |-- ivredb
  |-- ivredoku
  |-- ivreclient
```

---

## Ethical & Legal Guidelines

All tools installed here are for **defensive security and legitimate OSINT** only.

### Permitted Uses

- Verify if YOUR or YOUR CLIENT'S credentials have been exposed in breaches
- Anonymous scanning during **authorised** security assessments with written consent
- Dark web monitoring to check if client data has been leaked
- Network reconnaissance on networks you **own** or have **written authorisation** to test
- Competitive intelligence gathering from public sources

### Prohibited Uses

- Scanning networks without authorisation
- Accessing private systems via dark web
- Downloading or distributing stolen data
- Impersonation or social engineering
- Any activity that violates Australian law

### Australian Legal Framework

- **Criminal Code Act 1995, Part 10.7** — prohibits unauthorised access to computer systems
- **Surveillance Devices Act 2004** — restricts interception of communications
- **Privacy Act 1988** — governs handling of personal information
- **Cybercrime Act 2001** — criminalises unauthorised computer access

### Best Practices

1. **Always get written authorisation** before scanning any network or system
2. **Document everything** — keep logs of what was scanned and why
3. **Minimise data collection** — only collect what is necessary
4. **Secure findings** — encrypt and restrict access to OSINT results
5. **Report responsibly** — follow coordinated disclosure for vulnerabilities
6. **Respect privacy** — just because data is accessible does not mean it should be collected

---

## Troubleshooting

### Tor Proxy Not Connecting

```bash
# Check container is running
docker ps --filter name=tor-socks-proxy

# Check Tor bootstrap status
docker logs tor-socks-proxy 2>&1 | tail -10

# Should show: Bootstrapped 100% (done): Done
# If not, restart:
docker restart tor-socks-proxy
```

### Privoxy Not Forwarding

```bash
# Test directly
curl -x http://localhost:8118 https://check.torproject.org/api/ip

# If it fails, check the config
docker exec privoxy cat /etc/privoxy/config

# Verify the Tor link
docker exec privoxy ping -c 1 tor-socks-proxy
```

### IVRE Web UI Not Loading

```bash
# Check all 5 containers are running
docker ps --filter name=ivre

# If ivreweb keeps restarting, check logs
docker logs ivreweb 2>&1 | tail -20

# Common issue: ivredoku or ivreuwsgi not started yet
# Solution: wait 30 seconds and try again
```

### SpiderFoot Cannot Reach Tor

```bash
# Verify both are on osint-net
docker network inspect osint-net

# Test DNS resolution from SpiderFoot
docker exec spiderfoot python3 -c "import socket; print(socket.gethostbyname('tor-socks-proxy'))"

# If it fails, reconnect to network
docker network connect osint-net tor-socks-proxy
docker network connect osint-net spiderfoot
```

---

## Port Summary

| Port | Service | Protocol | Docker Container |
|------|---------|----------|------------------|
| 9050 | Tor SOCKS5 Proxy | SOCKS5 | `tor-socks-proxy` |
| 8118 | Privoxy HTTP Proxy | HTTP | `privoxy` |
| 8282 | IVRE Web UI | HTTP | `ivreweb` |
| 8284 | HIBP Offline Checker | HTTP/JSON | `hibp-checker` |
| 5009 | SpiderFoot | HTTP | `spiderfoot` |

---

*Made by Mani Padisetti @ Almost Magic Tech Lab*
*"Defensive security first. Always."*

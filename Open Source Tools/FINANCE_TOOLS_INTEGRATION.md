# FINANCE_TOOLS_INTEGRATION.md
## Almost Magic Tech Lab — Finance & Market Intelligence Stack
### Date: 13 February 2026

---

## What's Installed

### 1. FinceptTerminal (Desktop + CLI)

**Desktop App (Tauri v3.3.0)**
- Installed to `C:\Program Files\FinceptTerminal\fincept-terminal-desktop.exe`
- Desktop shortcut created
- Also in Start Menu: `FinceptTerminal`
- Launches as a native Windows desktop application
- No port — runs locally with its own embedded server

**CLI (Python, WSL2)**
- Installed in `~/fincept-env` virtual environment (Python 3.12)
- Package: `fincept-terminal` v2.0.8
- Activate: `source ~/fincept-env/bin/activate`
- Run: `fincept` (interactive TUI) or import as library
- Includes: yfinance, scholarly, selenium, duckdb, pandas, scipy

### 2. OpenBB (CLI, WSL2)

- Installed in same `~/fincept-env` virtual environment
- Package: `openbb` v4.6.0 with 30+ provider extensions
- Activate: `source ~/fincept-env/bin/activate`
- Use: `from openbb import obb`
- Providers available without API keys: Yahoo Finance, FRED, SEC, OECD, BLS, IMF, EconDB
- Providers requiring API keys (deferred): FMP, Polygon, Intrinio, Tiingo, Benzinga
- **No cloud API keys configured** — free data sources only

### 3. Ghostfolio (Docker, Port 3333)

- 3 containers: `ghostfolio`, `gf-postgres`, `gf-redis`
- Compose location: `~/ghostfolio/docker/docker-compose.yml`
- Environment: `~/ghostfolio/.env`
- Health endpoint: `http://localhost:3333/api/v1/health`
- First visit: `http://localhost:3333` to create admin account
- Own PostgreSQL (internal port 5432, no conflict with AMTL's 5433)
- Own Redis (cache only, RDB persistence disabled)
- restart: unless-stopped (auto-starts with Docker Desktop)

---

## Port Assignments

| Port | Service | Type | Health Check |
|------|---------|------|--------------|
| 3333 | Ghostfolio | Docker (Web) | `GET /api/v1/health` |
| — | FinceptTerminal Desktop | Native Windows App | N/A |
| — | FinceptTerminal CLI | WSL2 Python (~/fincept-env) | `python -c "import fincept_terminal"` |
| — | OpenBB CLI | WSL2 Python (~/fincept-env) | `python -c "from openbb import obb"` |

---

## Access URLs

| Tool | URL | Notes |
|------|-----|-------|
| Ghostfolio | http://localhost:3333 | Create admin account on first visit |
| FinceptTerminal | Desktop app | Double-click MSI to install, then launch from Start Menu |
| OpenBB | CLI only | `source ~/fincept-env/bin/activate && python` |
| FinceptTerminal CLI | CLI only | `source ~/fincept-env/bin/activate && fincept` |

---

## Registration

| Location | Status |
|----------|--------|
| Workshop (port 5003) | Registered — FinceptTerminal + Ghostfolio cards in `ck` section |
| Workshop backend | Registered — `fincept` + `ghostfolio` in SERVICES dict |
| Homepage (port 3011) | Registered — new "Market Intelligence" category with all 3 tools |
| Uptime Kuma (port 3001) | **Manual** — add Ghostfolio monitor: HTTP, `http://localhost:3333/api/v1/health`, 60s interval |

---

## How Oracle (AI CFO Module) Will Connect

Oracle is the planned AI Chief Financial Officer module for AMTL. It doesn't exist yet, but these tools establish the data foundation it will need. Here's the planned integration architecture:

### Data Flow 1: Market Data (FinceptTerminal/OpenBB -> Oracle Benchmarks)

```
FinceptTerminal CLI  ──┐
                       ├──> Oracle Benchmarks Table (PostgreSQL :5433)
OpenBB Platform     ──┘

Pipeline:
1. n8n scheduled workflow (daily, 7 AM AEST)
2. Activates ~/fincept-env, runs Python script
3. Fetches: ASX 200 index, AUD/USD rate, RBA cash rate, sector indices
4. OpenBB provides: economic indicators (FRED, OECD), company fundamentals
5. FinceptTerminal provides: technical analysis, market analytics
6. Writes to oracle_benchmarks table in PostgreSQL
7. Oracle queries this table for context when analysing Genie data
```

**Free data sources available now (no API keys):**
- Yahoo Finance: ASX stock prices, global indices, forex, crypto
- FRED: Interest rates, inflation, employment, GDP
- SEC: Company filings, insider trading
- OECD: Australian economic indicators
- BLS: Labour statistics
- IMF: International financial data
- EconDB: Economic datasets

### Data Flow 2: Portfolio Positions (Ghostfolio -> Oracle Investment Models)

```
Ghostfolio (:3333)  ──> Oracle Investment Decision Models

Pipeline:
1. Mani enters portfolio positions manually in Ghostfolio UI
2. Ghostfolio tracks: holdings, allocations, performance, dividends
3. Oracle reads via Ghostfolio REST API:
   - GET /api/v1/portfolio/positions — current holdings
   - GET /api/v1/portfolio/performance — returns over time
   - GET /api/v1/portfolio/dividends — income tracking
4. Oracle combines with market data to generate:
   - Rebalancing recommendations
   - Tax-loss harvesting opportunities (Australian CGT rules)
   - Dividend income forecasting
   - Currency exposure analysis (AUD portfolio with USD holdings)
```

### Data Flow 3: Cash Flow (Genie -> Oracle Forecasting)

```
Genie (:8000)  ──> Oracle Cash Flow Forecasting

Pipeline:
1. Genie captures: invoices, expenses, receipts, bank transactions
2. Oracle reads Genie's PostgreSQL tables directly (same :5433 instance)
3. Combined with market benchmarks, Oracle produces:
   - 90-day cash flow forecast
   - Revenue seasonality patterns
   - Expense trend analysis
   - Working capital recommendations
   - GST/BAS preparation data (Australian tax)
```

### Data Flow 4: Integrated Intelligence

```
All Sources  ──> Oracle Intelligence Layer  ──> ELAINE Morning Briefing

Combined outputs:
- "Revenue is up 12% but your AUD exposure is 40% — consider hedging"
- "ASX 200 down 3% this week but your consulting pipeline is strong"
- "BAS is due in 18 days — Genie shows $X GST collected, $Y GST paid"
- "Your portfolio is overweight tech — sector P/E is 28x vs historical 22x"

Oracle routes all LLM calls through Supervisor (:9000)
Uses Ollama (gemma2:27b or llama3.1:70b for complex analysis)
No cloud API keys — ever
```

---

## Architecture Diagram

```
                    +------------------+
                    |   ELAINE (:5000) |  <-- Morning Briefing includes finance summary
                    +--------+---------+
                             |
                    +--------v---------+
                    |  Oracle (planned) |  <-- AI CFO Module
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
    +---------v--+   +------v------+  +----v------+
    | Market Data |   | Portfolio   |  | Cash Flow |
    | Benchmarks  |   | Positions   |  | Forecast  |
    +------+------+   +------+------+  +-----+-----+
           |                 |               |
    +------v------+   +------v------+  +-----v-----+
    | OpenBB      |   | Ghostfolio  |  | Genie     |
    | FinceptTerm |   | (:3333)     |  | (:8000)   |
    | (~/fincept) |   +-------------+  +-----------+
    +-------------+

    All LLM calls route through Supervisor (:9000) -> Ollama (:11434)
    All data stored in PostgreSQL (:5433)
    No cloud API keys
```

---

## Maintenance

### Starting/Stopping Ghostfolio

```bash
# Via WSL2
cd ~/ghostfolio/docker
docker compose up -d      # Start
docker compose down        # Stop
docker compose logs -f     # View logs
```

### Updating

```bash
# Ghostfolio
cd ~/ghostfolio/docker
docker compose pull
docker compose up -d

# FinceptTerminal CLI + OpenBB
source ~/fincept-env/bin/activate
pip install --upgrade fincept-terminal openbb
```

### Verifying Health

```bash
# Ghostfolio
curl -s http://localhost:3333/api/v1/health
# Expected: {"status":"OK"}

# FinceptTerminal CLI
source ~/fincept-env/bin/activate
python -c "import fincept_terminal; print(fincept_terminal.__version__)"
# Expected: 2.0.5

# OpenBB
python -c "from openbb import obb; print('OpenBB OK')"
# Expected: OpenBB OK
```

---

## Known Issues

1. ~~FinceptTerminal MSI requires manual install~~ **RESOLVED** — installed to `C:\Program Files\FinceptTerminal\`, desktop shortcut created.
2. **Dependency conflicts in ~/fincept-env** — fincept-terminal pins `requests==2.31.0` and `yfinance==0.2.61`, OpenBB upgraded both. Both work fine despite pip warnings.
3. **Ghostfolio Redis persistence** — Disabled RDB snapshots (cache only). Data is in PostgreSQL, Redis is just for session caching.
4. **Uptime Kuma monitor** — Needs manual addition via web UI (WebSocket API, no REST).

---

*Made with care by Guruve @ Almost Magic Tech Lab*

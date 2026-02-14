# AMTL App Registry — 2026-02-15

## Application Inventory

| # | App | Folder | GitHub Repo | Port | Stack | Tests | Commit | Status |
|---|-----|--------|-------------|------|-------|-------|--------|--------|
| 1 | ELAINE (Chief of Staff) | Elaine-git | Almost-Magic/Elaine | 5000 | Python/Flask | Yes | `a5bf9a8` | Synced |
| 2 | Ripple CRM | Ripple CRM | Almost-Magic/ripple | 5002 | Node.js/Express | Yes | `44ce36d` | Synced |
| 3 | Identity Atlas | Identity Atlas | Almost-Magic/identity-atlas | 5002 | Node.js/Express | Yes | `dedaa96` | Synced |
| 4 | Learning Assistant | learning-assistant | Almost-Magic/learning-assistant | 5002 | Python/Flask | Yes | `bd34083` | Synced |
| 5 | CK Learning Asst | ck-learning-assistant | Almost-Magic/ck-learning-assistant | 5002 | Python/Flask | Yes | `bd34083` | Synced |
| 6 | CK-Writer | CK-Writer | Almost-Magic/CK-writer | 5008 | Node.js/Express | Yes | `383d97f` | Synced (node-rebuild) |
| 7 | Costanza | Costanza | Almost-Magic/costanza | 5001 | Node.js/Express | Yes | `f8b76a3` | Synced |
| 8 | Peterman | Peterman | Almost-Magic/peterman | 5008 | Node.js/Express | Yes | `120068d` | Synced |
| 9 | Genie v2.1 (AI Bookkeeper) | Finance App/Genie | Almost-Magic/genie | 5008 | Node.js/Express | Yes | `c7755ca` | Synced |
| 10 | Genie Legacy | Finance App/Genie-legacy | Almost-Magic/accounting-genie | N/A | Node.js/Electron | No | `dd6426c` | Synced |
| 11 | Digital Sentinel | Digital Sentinel | Almost-Magic/digital-sentinel | 5002 | Node.js/Express | Yes | `964ee2e` | Synced |
| 12 | The Ledger (AI Accountant) | The Ledger | Almost-Magic/the-ledger | 5002 | Node.js/Express | Yes | `b000bcb` | Synced |
| 13 | AI Safety Net | ai-safety-net | Almost-Magic/ai-safety-net | 3000 | Node.js/TypeScript | Yes | `79536f9` | Synced |
| 14 | Swiss Army Knife | Swiss Army Knife | Almost-Magic/ck-swiss-army-knife | 5000 | Python/Flask | No | `cbcb69b` | Synced |
| 15 | Opportunity Hunter | Opportunity Hunter | Almost-Magic/opportunity-hunter | 5006 | Python + React | No | `cad6517` | Synced |
| 16 | Junk Drawer | Junk Drawer file management system | Almost-Magic/junk-drawer | N/A | Node.js | No | `e0021a1` | Synced |
| 17 | AMTL TTS | amtl-tts | Almost-Magic/amtl-tts | 3000 | Node.js/TypeScript | Yes | `6813740` | Synced |
| 18 | AMTL Security | amtl-security | Almost-Magic/amtl-security | 8600 | Python/FastAPI | Yes | `bf6db09` | Synced |
| 19 | Signal | signal-git | Almost-Magic/Signal | N/A | Static | No | `f641822` | Synced |
| 20 | Signal v2 Semantic | signal-v2-semantic | Almost-Magic/signal-v2-semantic | N/A | Python | No | `00dc954` | Synced |
| 21 | Signal Desktop | signal-desktop | Almost-Magic/signal-desktop | N/A | Mixed | No | `2e92fda` | Synced |
| 22 | Beside You | beside-you | Almost-Magic/beside-you | N/A | Static HTML/JS | No | `48c8e14` | Synced |
| 23 | Dhamma Mirror | dhamma-mirror | Almost-Magic/dhamma-mirror | N/A | Node.js | Yes | `0066054` | Synced |
| 24 | Beast (Test Harness) | beast | Almost-Magic/beast | N/A | Python | No | `0d38b38` | Synced |
| 25 | Proof | proof | Almost-Magic/proof | 8000 | Python | No | `ebe0163` | Synced |
| 26 | Your Project Hub | your-project-hub | Almost-Magic/your-project-hub | N/A | Node.js | Yes | `0bdb533` | Synced |
| 27 | Your Project Setup | your-project-setup | Almost-Magic/your-project-setup | N/A | Node.js | Yes | `41fc839` | Synced |
| 28 | LLM Router | LLM-Orchestrator-git | Almost-Magic/llm-router | N/A | Python | No | `89520db` | Synced |
| 29 | Elaine Desktop | elaine-desktop | Almost-Magic/elaine-desktop | N/A | Electron | No | `06ae077` | Synced |
| 30 | The Workshop | workshop | (local only) | 5003 | Python/Flask | No | N/A | Local only |
| 31 | Hub (legacy) | Hub | (ck-hub — removed) | 5003 | Python/Flask | No | `7381021` | Dead remote |

## Non-Git Folders (Legacy/Manual)

| Folder | Contents |
|--------|----------|
| Elaine | Legacy Elaine (pre-v4), no git — preserved alongside Elaine-git |
| Author Studio | Manual files, no git (CK-Author-Studio repo is empty) |
| LLM-Orchestrator | Legacy files, no git — git clone at LLM-Orchestrator-git |
| signal | Legacy Signal files — git clone at signal-git |
| workshop | Local Flask app, no GitHub remote |
| ai-advisors | Manual files, no git |
| ck-desktop | Manual files, no git |
| desktop-apps | Manual files, no git |
| elaine-v3-phase1-2-3 | Archived Elaine v3 phases |

## Notes

- **CK-Writer** is on branch `node-rebuild` (default branch), not `main`
- **Hub** remote `ck-hub` no longer exists on GitHub — `your-project-hub` is the successor
- **Elaine-mobile** cloned but repo is empty (no commits)
- **CK-Author-Studio** cloned but repo is empty (no commits)
- Several apps share default ports — adjust when running simultaneously
- **Genie-legacy** (`accounting-genie`) is the Electron version; **Genie** is the v2.1 Node.js rebuild

## Quick Start Commands (PowerShell)

```powershell
$base = "C:\Users\ManiPadisetti\Dropbox\Desktop DB\Books and Articles Mani\Books\Almost Magic Tech Lab AMTL\Source and Brand\CK"

# ELAINE (Chief of Staff)
cd "$base\Elaine-git"; python app.py

# Ripple CRM
cd "$base\Ripple CRM"; node server.js

# Identity Atlas
cd "$base\Identity Atlas"; node server.js

# Learning Assistant
cd "$base\ck-learning-assistant"; python app.py

# CK-Writer
cd "$base\CK-Writer"; node server.js

# Costanza
cd "$base\Costanza"; node server.js

# Peterman
cd "$base\Peterman"; node server.js

# Genie v2.1
cd "$base\Finance App\Genie"; node server.js

# Digital Sentinel
cd "$base\Digital Sentinel"; node server.js

# The Ledger
cd "$base\The Ledger"; node server.js

# AI Safety Net
cd "$base\ai-safety-net"; npm start

# Swiss Army Knife
cd "$base\Swiss Army Knife"; python app.py

# Opportunity Hunter (backend)
cd "$base\Opportunity Hunter\backend"; python app.py

# AMTL TTS
cd "$base\amtl-tts"; node dist/server.js

# AMTL Security
cd "$base\amtl-security"; python main.py

# The Workshop
cd "$base\workshop"; python app.py

# Proof
cd "$base\proof"; python -m uvicorn server:app --port 8000
```

---
*Generated by Claudeman on 2026-02-15*

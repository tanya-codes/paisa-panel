# 🛡️ Paisa Panel — AI-Powered Stock Tip Verification Engine

<p align="center">
  <img src="assets/paisa-panel-logo-full.png" alt="Paisa Panel Logo" width="320" />
</p>

<p align="center">
  <strong>Don't invest blindly. Verify first.</strong><br/>
  An AI-powered 4-panel investigation engine that audits any stock tip, WhatsApp forward, or Telegram recommendation before you risk your hard-earned money.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/Frontend-Vanilla%20JS-F7DF1E?logo=javascript" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

## 🎯 What is Paisa Panel?

**Paisa Panel** is an AI stress-test engine for stock market tips. It takes any investment recommendation — from WhatsApp groups, Telegram channels, SMS forwards, or social media — and runs it through **4 independent expert panels** to determine whether the tip is trustworthy, suspicious, or an outright scam.

### The Problem It Solves

Every day, millions of retail investors in India receive stock tips via WhatsApp and Telegram. Many of these are **pump-and-dump schemes**, **unregistered advisory scams**, or **misleading forwards** that cause devastating financial losses. Paisa Panel gives everyday investors the tools that were previously available only to institutional analysts.

---

## 🏛️ The 4-Panel Council

Each stock tip is independently evaluated by four AI-powered expert personas:

| # | Panel | What It Checks |
|---|-------|---------------|
| 1 | **📊 The Claim Analyst** | Extracts what's actually being promised — target price, timeframe, upside — and checks if the numbers add up against real company financials |
| 2 | **⚖️ The Regulator's Eye** | Verifies if the source is SEBI-registered, checks for PFUTP (fraud) violations, and flags illegal guaranteed-return promises |
| 3 | **📈 The Market Historian** | Looks at what actually happened to the stock after similar tips in the past — exposing pump-and-dump patterns |
| 4 | **🔍 The Source Auditor** | Investigates who sent the tip — verified institutional research or anonymous unregistered channel? |

After all 4 panels deliberate, the **Council's Verdict** delivers a trust score (0–100) with clear red flags and green signals.

---

## ✨ Key Features

- **🔐 Login Screen** — Professional Google/email sign-in with guest demo access
- **📝 Claim Intake** — Paste any stock tip text and submit for investigation
- **🎭 4-Panel Live Deliberation** — Watch each expert analyze the claim in real-time with streaming SSE updates
- **⚡ 5-Entity Separation** — Strictly distinguishes CLAIM vs SOURCE vs SECURITY vs REGULATORY STATUS vs EVIDENCE (never conflates them)
- **📊 Quantitative Trust Score** — Animated gauge with detailed factor-by-factor breakdown
- **🏛️ Council Verdict** — Final assessment with red flags, green signals, and bilingual (English/Hindi) support
- **📋 Dashboard** — History of all analyzed claims with re-test capability
- **🔬 Pattern Detection** — Identifies guaranteed-return language, urgency/FOMO tactics, and unregistered advisory patterns
- **👥 Community Court** — Crowd-sourced suspicion ratings and platform circulation data
- **🌐 Bilingual** — Full English and Hindi language support

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│  index.html + app.js + services.js + styles.css  │
│          (Vanilla JS, SSE streaming)             │
└──────────────────────┬──────────────────────────┘
                       │ POST /api/analyze/stream
                       ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend (server.py)          │
│                                                   │
│  ┌─────────────┐  ┌──────────────────────────┐   │
│  │ Claim        │  │ 4-Persona Source Engine   │   │
│  │ Extraction   │  │ (get_persona_sources)     │   │
│  └──────┬──────┘  └────────────┬─────────────┘   │
│         │                      │                   │
│         ▼                      ▼                   │
│  ┌──────────────────────────────────────────┐     │
│  │     Scoring Engine (scoring_engine.py)    │     │
│  │  • compute_exact_score()                  │     │
│  │  • identify_source_entity()               │     │
│  │  • detect_certainty_and_urgency()         │     │
│  │  • find_matched_asset()                   │     │
│  └──────────────────────────────────────────┘     │
│                      │                             │
│                      ▼                             │
│  ┌──────────────────────────────────────────┐     │
│  │     Council Verdict Builder               │     │
│  │  (build_council_verdict)                  │     │
│  └──────────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/tanya-codes/paisa-panel.git
cd paisa-panel

# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

The app will be running at **http://127.0.0.1:4173**

### Running Tests

```bash
# Run the full 9-case verification engine regression suite
python test_verification_engine.py
```

All 9 test cases (A–I) cover:
- ✅ Verified institutional research (Goldman Sachs on HAL)
- ❌ Anonymous Telegram pump-and-dump schemes
- ❌ SEBI-documented fraud cases (Darshan Orna)
- ⚠️ Mixed claims (real research + fake guarantees)
- ⚠️ Missing evidence handling
- 🔍 Entity resolution disambiguation
- 🔍 Unidentified source objectivity
- ⚠️ WhatsApp tips (IRFC)
- ⚠️ Institutional brokerage calls (Pine Labs / Motilal Oswal)

---

## 📁 Project Structure

```
paisa-panel/
├── server.py                    # FastAPI backend — claim extraction, 4-persona engine, SSE streaming
├── scoring_engine.py            # Quantitative scoring — trust score computation, entity resolution
├── index.html                   # Single-page application — login, intake, analysis, verdict, dashboard
├── app.js                       # Frontend logic — UI state, animations, persona cards, score rendering
├── services.js                  # Investigation service — evidence caching, source lookups
├── styles.css                   # Complete design system — responsive, dark/light, animations
├── test_verification_engine.py  # 9-case automated regression test suite
├── requirements.txt             # Python dependencies
├── assets/
│   ├── paisa-panel-logo-full.png
│   ├── paisa-panel-favicon.png
│   ├── paisa-panel-mark.png
│   └── paisa-panel-original.png
└── README.md
```

---

## 🧪 How the Scoring Works

The trust score (0–100) is computed by `scoring_engine.py` using weighted factors:

| Factor | Weight | What It Measures |
|--------|--------|-----------------|
| Source Credibility | 25 pts | SEBI registration, institutional backing, author verification |
| Claim Plausibility | 20 pts | Is the target price realistic given company financials? |
| Regulatory Compliance | 20 pts | Any PFUTP violations, illegal guarantees, missing disclosures? |
| Evidence Quality | 15 pts | Strength and recency of supporting evidence |
| Historical Precedent | 10 pts | What happened to similar tips in the past? |
| Transparency | 10 pts | Stop-loss mentioned? Risk disclosures present? |

### Score Interpretation

| Score | Verdict | Meaning |
|-------|---------|---------|
| 80–100 | ✅ VERIFIED | Backed by credible institutional research with proper disclosures |
| 50–79 | ⚠️ PARTIALLY VERIFIED | Some legitimate elements but with unverified claims or missing disclosures |
| 25–49 | ⚠️ UNVERIFIED | Lacks credible evidence; exercise extreme caution |
| 0–24 | ❌ CONTRADICTED | Contradicted by regulatory orders, known scam patterns, or fraudulent language |

---

## 🔒 5-Entity Separation Rule

Paisa Panel strictly separates five entities to prevent dangerous conflation:

1. **CLAIM** — The exact statement being made
2. **SOURCE** — Who published/forwarded the recommendation
3. **SECURITY** — The stock/instrument being recommended (this is NOT the adviser)
4. **REGULATORY STATUS** — SEBI registration status of the SOURCE
5. **EVIDENCE PROVIDER** — SEBI, NSE, BSE — factual record providers, NOT the recommendation source

> **Critical**: SEBI is never treated as the recommendation source. A stock being investigated by SEBI doesn't mean SEBI recommended it.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI, Uvicorn, httpx |
| Frontend | Vanilla JavaScript, HTML5, CSS3 |
| Streaming | Server-Sent Events (SSE) |
| Fonts | Inter, Plus Jakarta Sans, JetBrains Mono (Google Fonts) |
| Data Sources | SEBI enforcement orders, NSE/BSE filings, Screener.in |

---

## 📜 Disclaimer

> **Paisa Panel is an educational demonstration tool.** It is NOT financial advice. The analysis is illustrative and should not be the sole basis for any investment decision. Always consult a SEBI-registered investment advisor before making financial decisions.

---

## 👩‍💻 Author

**Tanya Sharma**  
Built with ❤️ to protect everyday Indian investors from stock market fraud.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

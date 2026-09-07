# ðŸŒ¾ FreshOps AI â€” Operational Intelligence & Cold-Chain Hub (`week10_ops_tool`)

> **Week 10 AI-Powered Operational Tool & Product Demo Deliverable**  
> **Author & Lead Developer:** Kelvin Moruri  
> **Capstone Project:** fresh-supplies  
> An AI-engineered operational cockpit for fresh produce logistics, automated cold-chain breach detection, dynamic wholesale market rerouting, and real-time loss mitigation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Pytest](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ðŸ“Œ 1. The Operational Problem

In East Africa's agricultural value chain, **up to 40% of fresh horticultural produce** (tomatoes, avocados, mangoes, bananas) is lost between farm gate and consumer markets. The two primary operational causes are:
1. **Unnoticed Cold-Chain Breaches:** Refrigeration breakdowns and excessive thermal exposure (>15Â°C) rapidly accelerate decay during transit.
2. **Inflexible Dispatch Routing:** When trucks face unexpected delays (>16 hours) heading to distant destinations (e.g., Nairobi Gikomba or Mombasa Kongowea), dispatchers lack real-time price and distance visibility to divert cargo to nearer wholesale hubs, resulting in total crop loss and lost farmer income.

**FreshOps AI** resolves this with an automated operational decision engine that marries live telemetry monitoring, AI-guided market diversion, and instant executive reporting.

---

## ðŸš€ 2. Core Capabilities & Feature Tour

### ðŸ›°ï¸ Tab 1: Live Fleet & Cold-Chain Radar
- **Geospatial Transit Map:** Plotly interactive map rendering 10,000 shipment telemetry records across Kenyan road networks, color-coded by AI Spoilage Risk Tier (`CRITICAL`, `AT_RISK`, `FRESH`).
- **Cargo Thermal Profile:** Real-time distribution histogram comparing cargo temperatures against the 15Â°C critical threshold.
- **Urgent Breach Queue:** Automatically surfaces trucks requiring immediate ice reinforcement or mechanic dispatch.

### ðŸ”„ Tab 2: Dynamic Market Rerouting Simulator
- **What-If Scenario Sliders:** Simulate added transit delays (+0 to +8 hrs) or cooling interventions (-5Â°C to +5Â°C) to recalculate risk.
- **Wholesale Price Arbitrage:** Ranks 10 major wholesale destinations (Nairobi, Nakuru, Kisumu, Mombasa, Eldoret, Thika, Meru, Kakamega, Naivasha, Bomet) based on distance, estimated travel time, and wholesale crop price.
- **Revenue Salvage Calculation:** Calculates net retainable revenue per 100 kg batch, enabling dispatchers to salvage over 75% of otherwise lost cargo value.
- **1-Click Diversion Order:** Authorizes driver reroute orders with simulated broadcast confirmations.

### ðŸ¤– Tab 3: AI Ops Copilot (Dual-Mode Intelligence)
- **Online Mode (Google Gemini 1.5 Flash):** When `GEMINI_API_KEY` is provided in `.env`, generates real-time, context-grounded operational briefings.
- **Offline Mode (Deterministic Semantic NLP Engine):** Runs 100% locally with zero configuration. Accurately answers inquiries on temperature breaches, crop vulnerabilities, revenue at risk, and corridor status without crashing.
- **Quick-Prompt Chips:** Pre-built buttons for instant dispatcher diagnostics.

### ðŸ“‘ Tab 4: Automated Incident Reporting & Dispatch Alerts
- **1-Click Executive PDF Generator:** Creates a professional, styled audit report (`reports/daily_ops_report.pdf`) using ReportLab, complete with KPI summaries, top at-risk batches, and Standard Operating Procedures (SOP).
- **Driver SMS / WhatsApp Alert Formatter:** Pre-fills standardized emergency dispatch notifications for immediate relay to drivers.
- **Audit CSV Export:** Download filtered shipment subsets for enterprise ERP integration.

---

## ðŸ—ï¸ 3. Project Architecture

```
week10_ops_tool/
â”‚
â”œâ”€â”€ app.py                     # Streamlit frontend & interactive dashboard
â”œâ”€â”€ ops_engine.py              # Core analytics, haversine math, AI copilot, PDF engine
â”œâ”€â”€ requirements.txt           # Pinned production dependencies
â”œâ”€â”€ pytest.ini                 # Pytest runner configuration
â”œâ”€â”€ .env.example               # Environment template (zero hardcoded secrets)
â”œâ”€â”€ .env                       # Local environment file (git-ignored)
â”œâ”€â”€ .gitignore                 # Security rules ignoring credentials and cache
â”‚
â”œâ”€â”€ data/                      # Production operational datasets
â”‚   â”œâ”€â”€ food_scored.csv        # 10,000 scored shipments with telemetry & coordinates
â”‚   â”œâ”€â”€ market_prices.csv      # Real-time wholesale prices across 10 Kenyan hubs
â”‚   â””â”€â”€ market_destinations.csv# GPS coordinates and metadata of wholesale markets
â”‚
â”œâ”€â”€ tests/
â”‚   â””â”€â”€ test_ops_tool.py       # Automated unit test suite (5/5 passing)
â”‚
â”œâ”€â”€ reports/                   # Destination directory for generated PDF audits
â”‚
â”œâ”€â”€ PROMPTS.md                 # Complete Vibe Coding prompt engineering log
â”œâ”€â”€ README.md                  # Comprehensive platform documentation
â”œâ”€â”€ Week10_Product_Demo_Script.md # 3-minute video presentation script
â”œâ”€â”€ demo_slides.html           # Presentation slide deck for demo recording
â”œâ”€â”€ LINKEDIN_POST.md           # Professional LinkedIn promotion post draft
â””â”€â”€ capstone_week10_update.md  # Capstone integration report for fresh-supplies
```

---

## âš¡ 4. Quickstart Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Modern web browser (Chrome, Edge, Firefox)

### Step 1: Clone or Navigate to Directory
```bash
cd "c:\projects\EMT\plp\AI-Powered Operational Tool & Product Dem"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
Copy the `.env.example` template:
```bash
cp .env.example .env
```
*(Optional)* If you have a Google Gemini API Key, add it to `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
```
> **Note:** An API key is **optional**. The tool includes a built-in deterministic Semantic NLP Engine that operates 100% offline out-of-the-box!

### Step 4: Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ðŸ§ª 5. Running Automated Tests

Run the complete pytest test suite:
```bash
pytest -v
```
Expected output:
```
tests/test_ops_tool.py::test_data_ingestion_and_flags PASSED             [ 20%]
tests/test_ops_tool.py::test_kpi_calculations PASSED                     [ 40%]
tests/test_ops_tool.py::test_market_diversion_ranking PASSED             [ 60%]
tests/test_ops_tool.py::test_ops_copilot_offline_reasoning PASSED        [ 80%]
tests/test_ops_tool.py::test_pdf_report_generation PASSED                [100%]
============================== 5 passed in 3.42s ==============================
```

---

## ðŸ”’ 6. Security & Best Practices
- **Zero Hardcoded Secrets:** All configurations, API keys, and file paths are managed via `.env` and `python-dotenv`.
- **Git Security:** `.env` is explicitly declared in `.gitignore`.
- **Defensive Data Handling:** Input coordinates, temperatures, and durations are validated and sanitized to prevent NaN or division-by-zero crashes.
- **Fail-Safe AI Architecture:** Network failures or missing API tokens gracefully degrade to deterministic offline analytics with zero downtime.

---

## ðŸ¤ 7. Capstone Integration Link

This tool is directly connected to the **`fresh-supplies`** capstone repository located at `C:\projects\EMT\fresh-supplies`. See [`capstone_week10_update.md`](capstone_week10_update.md) for full details on how this vibe-coded operational engine integrates into the broader post-harvest data engine on branch `develop`.
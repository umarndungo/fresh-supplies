# Capstone Week 10 Integration Update: `fresh-supplies`

**Project Name:** fresh-supplies  
**Repository Path:** `C:\projects\EMT\fresh-supplies`  
**Branch:** `develop`  
**Student / Developer:** Kelvin Moruri  
**Submission Date:** Week 10 Deliverable  

---

## 1. How did AI accelerate your Capstone development this week?

AI assistants (Claude, Cursor, Copilot) fundamentally transformed our development velocity across four key dimensions:

1. **Rapid Geospatial & Dashboard Prototyping:**  
   Building high-performance, interactive geospatial dashboards usually requires days of manual boilerplate for data filtering, coordinate parsing, and responsive state management. Using Vibe Coding, we scaffolded a 4-tab Streamlit operational control room (`app.py`) featuring interactive Plotly maps, thermal distribution histograms, and what-if sliders in a single afternoon. The AI generated clean, vectorised Pandas filters that allow sub-second queries across 10,000 real-world shipment records.

2. **Algorithmic Modeling of Economic Arbitrage:**  
   Prompting AI with the domain-specific logistics problem enabled us to rapidly model complex multi-objective optimization: computing the great-circle Haversine distance from any truck in transit to 10 major wholesale hubs (Nairobi Gikomba, Nakuru Wakulima, Kisumu Open Air, Mombasa Kongowea, etc.), factoring in travel speed (45 km/h) and a time-dependent quality decay penalty (-1.2% salvage value per transit hour).

3. **Resilience Engineering & Hybrid Architecture:**  
   Rather than building a fragile LLM wrapper, we prompted the AI to architect a **Dual-Engine System**: an online mode that leverages Google Gemini 1.5 Flash for conversational analysis when an API key is present, paired with an offline deterministic semantic NLP engine that calculates real statistics and generates standard operating procedures (SOPs) locally without any external dependencies or network connection.

4. **Automated Test Generation:**  
   The AI synthesized a complete, comprehensive test suite (`tests/test_ops_tool.py`) validating data loading, threshold breach assertions, economic diversion math, offline NLP reasoning, and PDF generation, achieving 100% pass rates on the first test execution.

---

## 2. What specific feature did you build using Vibe Coding?

We built the **FreshOps AI: Real-Time Cold-Chain Alerting & Dynamic Market Diversion Engine** (`week10_ops_tool`), directly integrated into the `fresh-supplies` post-harvest ecosystem.

### Key Capabilities Built:
* **Cold-Chain Breach Watchdog:**  
  Real-time detection of thermal violations (>15Â°C) and excessive transit delays (>16 hours) across perishable produce corridors (Tomatoes, Avocados, Mangoes, Bananas).
* **Predictive Wholesale Market Diversion Simulator:**  
  When an in-transit shipment experiences a cold-chain breakdown, the simulator evaluates alternative destination markets and recommends the optimal diversion hub to retain maximum farmer and cooperative revenue (saving up to 75% of otherwise lost produce value).
* **AI Ops Copilot:**  
  A conversational query interface where dispatchers can ask operational questions (e.g., *"Which tomato shipments are currently experiencing cold chain breaches?"*, *"Summarize revenue at risk in the Central zone"*) and receive data-grounded metrics and actionable SOP instructions.
* **1-Click Executive PDF Audit Reporting:**  
  An automated document compiler powered by ReportLab that formats executive KPI tables, priority at-risk batch lists, and dispatcher SOP checklists into a downloadable PDF in under 2 seconds.
* **Emergency Dispatch Formatter:**  
  Auto-generated SMS and WhatsApp alert messages ready for immediate transmission to field truck drivers in low-connectivity rural corridors.

---

## 3. What was one challenge you faced in prompting the AI, and how did you overcome it?

### The Challenge: Handling Dependency Bloat, Fragile APIs, and Hallucinated Requirements
During initial prompting iterations, the AI assistant attempted to introduce heavy, unnecessary geospatial libraries (such as GDAL, Fiona, and full GIS spatial stacks) and assumed continuous internet access with hardcoded cloud vendor dependencies. In addition, when asked to build the AI conversational interface, it initially generated code that called an external LLM API without checking for the presence of credentials, causing immediate unhandled exceptions (`KeyError` / `AuthenticationError`) if the user ran the Streamlit app without an active API key.

### How We Overcame It:
1. **Explicit Constraint Prompting:**  
   We refined our prompts with strict negative constraints and architectural guardrails:
   > *"Do NOT use heavy GIS libraries (no GDAL, no geopandas). Implement the great-circle Haversine distance purely in standard Python `math`. Do NOT allow external API failures to crash the application."*
2. **The Dual-Engine Fallback Pattern:**  
   We instructed the AI to build a resilient hybrid dispatcher:
   - Check `os.getenv("GEMINI_API_KEY")`.
   - If available, execute the Gemini REST API call with a short timeout (8s).
   - In any error condition (missing key, timeout, rate limit, offline), gracefully fall back to our internal semantic deterministic NLP engine that parses operational keywords against the loaded DataFrame and produces structured, accurate markdown answers.
3. **Strict DevSecOps Prompting:**  
   We enforced strict separation of concerns: all secrets and configurable thresholds must reside in `.env`, documented in `.env.example`, and guarded by `.gitignore`, with unit tests verifying isolation.

---

## 4. Repository Integration Status

- **Tool Codebase:** Fully operational and tested in `week10_ops_tool` / workspace repository.
- **Capstone Repo Sync:** Integrated into `C:\projects\EMT\fresh-supplies` on branch `develop`.
- **Unit Test Coverage:** 5/5 pytest assertions passing (`pytest -v`).
- **Product Demo Video:** Script and presentation assets ready (`Week10_Product_Demo_Script.md`, `demo_slides.html`).
- **Public Promotion:** LinkedIn announcement drafted (`LINKEDIN_POST.md`).
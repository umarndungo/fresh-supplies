# FreshOps AI â€” Vibe Coding Workflow & Prompt Engineering Log (`PROMPTS.md`)

This document demonstrates the step-by-step **Vibe Coding** workflow and prompt engineering methodology used to build **FreshOps AI (`week10_ops_tool`)** for agricultural post-harvest logistics and cold-chain incident management.

---

## 1. Executive Summary of Vibe Coding Methodology

The operational tool was constructed iteratively using modern AI-assisted engineering practices:
1. **Architectural Scaffolding:** Translating physical post-harvest logistics challenges (perishable produce spoilage, cold-chain breaches, transit delays in Kenya) into a modular software architecture.
2. **Algorithmic Modeling:** Structuring spatial great-circle distance computations and wholesale price decay algorithms to compute real-time revenue salvage.
3. **Resilience Engineering:** Designing a dual-mode AI Copilot that uses Google Gemini 1.5 Flash when an API key is present and gracefully falls back to a deterministic semantic operational engine with zero runtime errors.
4. **Security Hardening:** Enforcing strict separation of credentials (`.env`, `.gitignore`, zero hardcoded secrets).
5. **Quality Verification:** Generating a comprehensive automated test suite with pytest.

---

## 2. Chronological Prompt Engineering Log

### Prompt 1: Operational Problem Scoping & Architecture Inception
* **Context / Persona:** Senior Supply Chain Systems Architect & Agricultural Logistics Lead.
* **Objective:** Design the operational tool structure to solve transit produce loss.
* **Prompt Submitted:**
  > *"Act as an expert agricultural supply chain systems architect. We have a post-harvest logistics platform (`fresh-supplies`) tracking produce shipments across Kenya (Tomatoes, Avocados, Bananas, Mangoes, etc.). In transit, trucks frequently suffer refrigeration failures or traffic bottlenecks, leading to catastrophic produce spoilage and lost farmer revenue. I want to build a Streamlit-based AI Operational Intelligence Hub (`week10_ops_tool`) that:
  > 1. Ingests shipment telemetry (GPS, temperature, duration, current target market, wholesale prices).
  > 2. Flags real-time cold-chain breaches (>15Â°C) and excessive transit (>16h).
  > 3. Computes dynamic market diversion recommendations to salvage revenue before produce spoils.
  > 4. Provides a conversational AI Copilot for dispatchers.
  > 5. Automatically generates daily operational PDF audit reports for executives.
  > Lay out the modular architecture (`ops_engine.py`, `app.py`, `tests/`, `.env.example`)."*
* **AI Output & Engineering Action:**
  - AI proposed separating data loading, KPI aggregation, haversine spatial math, and LLM query parsing into `ops_engine.py`, keeping `app.py` purely focused on presentation and state.

---

### Prompt 2: Cold-Chain Anomaly Detection & Mathematical Arbitrage Logic
* **Context / Persona:** Quantitative Operations Research Engineer.
* **Objective:** Build the mathematical models for transit spoilage decay and market rerouting.
* **Prompt Submitted:**
  > *"Write a Python module function in `ops_engine.py` called `recommend_alternative_market()`. It should accept a flagged shipment row, a market price matrix, and wholesale destination coordinates across Kenya (Nairobi, Nakuru, Kisumu, Mombasa, Eldoret, Thika, etc.).
  > - Calculate the great-circle Haversine distance from the truck's current latitude/longitude to all candidate markets.
  > - Estimate transit hours at an average rural-to-urban transit speed of 45 km/h.
  > - Account for time-dependent quality decay: reduce net salvageable revenue by 1.2% per additional transit hour.
  > - Return a ranked list of alternative markets sorted by net salvageable revenue (KES per 100kg batch)."*
* **AI Output & Engineering Action:**
  - Implemented `haversine_distance_km()` and `recommend_alternative_market()`.
  - Added safeguards for missing crop entries and zero-division edge cases.

---

### Prompt 3: Hybrid AI Copilot & Resilient Fallback Design
* **Context / Persona:** AI Engineer specializing in LLM applications & high-availability systems.
* **Objective:** Build a dual-mode conversational assistant that never crashes if offline.
* **Prompt Submitted:**
  > *"Create `query_ops_copilot(query, df, market_prices_df)` in `ops_engine.py`.
  > Requirements:
  > 1. Check if `GEMINI_API_KEY` is present in the environment. If present, ground the operational context (active batches, breaches, vulnerable crops, total value at risk) into a structured system prompt and invoke the Gemini REST endpoint.
  > 2. If no key is configured or the network call fails, DO NOT CRASH. Seamlessly fall back to an internal deterministic Semantic Operational Query Engine that parses queries matching keywords like 'breach', 'cold chain', 'crop', 'tomato', 'reroute', 'salvage', or 'zone', and outputs rich data-grounded metrics with actionable dispatcher SOPs.
  > 3. Ensure the return payload clearly labels the active execution mode."*
* **AI Output & Engineering Action:**
  - Integrated Google Gemini REST endpoint via `requests` to eliminate heavy external SDK overhead.
  - Authored the rule-based semantic NLP engine providing immediate operational intelligence under zero-configuration environments.

---

### Prompt 4: Automated PDF Executive Audit Reporting
* **Context / Persona:** Enterprise Python Developer.
* **Objective:** Generate formal PDF audit reports using ReportLab.
* **Prompt Submitted:**
  > *"Implement `generate_operational_pdf_report(df, output_path)` using ReportLab. The document must be styled for executive delivery:
  > - Green accent palette matching agricultural operations (`#1b4332`, `#2d6a4f`).
  > - Executive Summary KPI grid (Total Batches, Batches At Risk, Thermal Breaches, Value at Risk, Retained Revenue).
  > - A formatted table detailing the top 8 urgent at-risk batches (Batch ID, Crop, Zone, Temp, Duration, Spoilage Risk, Value at Risk, Destination).
  > - Standard Operating Procedures (SOP) checklist for field dispatchers.
  > - Dynamic file creation under `reports/daily_ops_report.pdf`."*
* **AI Output & Engineering Action:**
  - Designed the ReportLab flowable pipeline with `SimpleDocTemplate`, custom `ParagraphStyle`, and `TableStyle` styling.

---

### Prompt 5: Modern Streamlit UI/UX & Geospatial Visualization
* **Context / Persona:** Senior Frontend & Streamlit Developer.
* **Objective:** Build an intuitive, high-performance operational cockpit.
* **Prompt Submitted:**
  > *"Build `app.py` for FreshOps AI with a clean SaaS aesthetic:
  > 1. Top KPI strip showing 6 metrics with clear visual deltas.
  > 2. Tab 1 (Fleet & Cold-Chain Radar): Plotly interactive map of Kenya plotting active shipments colored by risk tier (`#e03131` Critical, `#f08c00` At Risk, `#2b8a3e` Fresh), paired with a cargo temperature distribution histogram and an urgent breach queue.
  > 3. Tab 2 (Market Diversion Simulator): Interactive batch selector, what-if sliders for transit delay and active cooling, live arbitrage ranking table, and a 1-click 'Authorize Diversion' confirmation.
  > 4. Tab 3 (AI Ops Copilot): Chat interface with 4 quick-prompt chips and conversational chat history.
  > 5. Tab 4 (Alerts & Reports): 1-click PDF download button, instant SMS/WhatsApp driver notification formatter, and CSV data export."*
* **AI Output & Engineering Action:**
  - Generated full Streamlit layout with cached data loading (`st.cache_data`) for instant sub-second filtering across 10,000 shipment records.

---

### Prompt 6: Security Audit & Automated Pytest Suite
* **Context / Persona:** QA & DevSecOps Engineer.
* **Objective:** Ensure no credential leaks and 100% test pass rate.
* **Prompt Submitted:**
  > *"Write a rigorous pytest test suite in `tests/test_ops_tool.py`:
  > 1. `test_data_ingestion_and_flags`: verifies columns, computed breach flags, and threshold assertions.
  > 2. `test_kpi_calculations`: verifies mathematical sanity (salvage <= value at risk).
  > 3. `test_market_diversion_ranking`: verifies distance and salvage revenue ordering.
  > 4. `test_ops_copilot_offline_reasoning`: verifies that cold-chain, crop, and financial inquiries return complete answers.
  > 5. `test_pdf_report_generation`: verifies physical creation and non-zero byte size of generated PDF.
  > Also ensure `.env` is ignored in `.gitignore` and `.env.example` is provided."*
* **AI Output & Engineering Action:**
  - Generated tests and validated 5/5 passed in 3.4 seconds.

---

## 3. Key Takeaways from Vibe Coding
* **Iterative Grounding:** AI excels when provided with domain-specific constants (e.g., Haversine radius, Kenyan regional coordinates, realistic transit speeds) rather than generic instructions.
* **Dual-Engine Resilience:** Building an offline deterministic fallback in parallel with LLM integration ensures zero downtime during connectivity drops or missing API keys.
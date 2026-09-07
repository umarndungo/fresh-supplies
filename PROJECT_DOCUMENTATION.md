# Fresh Supplies (FreshRoute AI)
## Intelligent Post-Harvest Logistics & Dynamic Cold-Chain Spoilage Mitigation Engine

> **Mitigating Sub-Saharan Perishable Food Loss Through Predictive Machine Learning, Real-Time Telemetry Watchdogs, and Algorithmic Market Diversion**

---

## 1. Executive Summary & Problem Statement

### The Post-Harvest Perishable Crisis in Sub-Saharan Africa
In Sub-Saharan Africa—and across Kenya's key agricultural corridors (from the Rift Valley and Western highlands to Central Kenya)—**between 30% and 40% of all harvested horticultural produce is lost before ever reaching a consumer**. 

Smallholder farmers and agricultural cooperatives lose millions of Kenyan Shillings (KES) annually not because of poor harvest yields, but due to **logistical blindness during transit**:
- **Thermal Heat Exposure:** Perishable produce (tomatoes, avocados, mangoes, bananas, leafy vegetables) is routinely transported in uninsulated, non-refrigerated trucks where ambient cabin temperatures exceed 25°C–32°C, drastically accelerating microbial decay and respiration rates.
- **In-Transit Delays & Road Bottlenecks:** Feeder road congestion, mechanical breakdowns, and checkpoint holdups cause transit durations to stretch beyond 16–24 hours, converting prime produce into unsellable waste.
- **Static, Inflexible Routing:** Drivers are locked into predetermined destinations (e.g., navigating 400+ km to Nairobi or Mombasa). Even when the cargo begins to deteriorate mid-journey, drivers lack the visibility and market intelligence required to divert cargo to nearer, high-demand secondary wholesale hubs.
- **Information Asymmetry:** Cooperative dispatchers and farmers have zero real-time visibility into cargo health, resulting in total write-offs at destination markets upon delivery inspection.

### The Fresh Supplies Mission
**Fresh Supplies (FreshRoute AI)** was engineered to turn transit blindness into actionable, real-time economic protection. By fusing **IoT thermal/transit telemetry**, **supervised machine learning (XGBoost/RandomForest)**, and **spoilage-aware graph optimization (NetworkX)**, Fresh Supplies continuously monitors produce health in transit and computes optimal dynamic market diversions—**salvaging up to 75% of economic value that would otherwise be permanently lost**.

---

## 2. Core Value Proposition & Operational Impact

```
                    +----------------------------------------+
                    |  In-Transit Sensor & GPS Telemetry     |
                    |  Temp (°C), Vibration, Transit Time,   |
                    |  Crop Frailty Index, Ambient Humidity  |
                    +-------------------+--------------------+
                                        |
                                        v
                    +----------------------------------------+
                    |       FastAPI & ML Inference Engine    |
                    |   Predictive Spoilage Risk (0 - 100%)  |
                    |   SMOTE + XGBoost / Random Forest      |
                    +-------------------+--------------------+
                                        |
            +---------------------------+---------------------------+
            |                                                       |
   [ Spoilage < 15% ]                                     [ Spoilage >= 15% ]
        STATUS: FRESH                                      STATUS: AT_RISK / CRITICAL
            |                                                       |
            v                                                       v
+-----------------------+                         +-----------------------------------+
|  Maintain Primary     |                         | Algorithmic Market Diversion      |
|  Corridor Destination |                         | NetworkX Friction Score (Time +   |
|  (Max Target Margin)  |                         | Spoilage + Transit Road Cost)     |
+-----------------------+                         +-----------------+-----------------+
                                                                    |
                                                                    v
                                                  +-----------------------------------+
                                                  | 10 Wholesale Regional Hubs Ranked |
                                                  | Optimal Revenue Retained Selected |
                                                  | Auto Dispatch to Driver (SMS/App) |
                                                  +-----------------------------------+
```

### How Fresh Supplies Solves the Crisis:
1. **Real-Time Spoilage Risk Forecasting (`/predict-spoilage`):**  
   Evaluates incoming transit duration, temperature exposure, barometric pressure, distance to destination, and crop-specific frailty to classify cargo into clear operational risk tiers:
   - **`FRESH` (Spoilage < 15%):** Cargo is healthy; proceed along planned primary transit route.
   - **`AT_RISK` (Spoilage 15% – 25%):** Spoilage threshold breached; initiate early warning and prepare diversion options.
   - **`CRITICAL` (Spoilage > 25%):** Imminent cargo failure; trigger emergency reroute to the nearest high-salvage wholesale market.

2. **Dynamic Wholesale Market Diversion (`/recommend-market`):**  
   When a cold-chain breach occurs, the system models the multi-modal trade-off between additional transit time, quality decay penalties, and prevailing wholesale market prices across **10 major Kenyan agricultural markets**, instantly calculating the route that maximizes farmer payout.

3. **Multi-Role Collaborative Operations:**  
   Empowers **Farmers**, **Agricultural Cooperatives**, **Truck Drivers**, and **Market Off-Takers** through dedicated dashboards, automated batch labeling, CSV audit export, and low-bandwidth rural alert formats (SMS/WhatsApp formats).

---

## 3. Hard Numbers & Tested Quantitative Metrics

| Metric Dimension | Quantified Value | Description & Verification |
| :--- | :--- | :--- |
| **Model Classification Quality** | **ROC-AUC ~ 0.87** | Stratified 5-fold cross-validated XGBoost and Random Forest pipeline with embedded SMOTE over-sampling. |
| **Produce Value Retained** | **Up to 75%** | Economic value preserved on degraded batches via dynamic wholesale market diversion vs. total write-off. |
| **Telemetry Training Volume** | **10,000+ records** | Multi-zone agricultural shipment dataset featuring temperature, pressure, transit duration, and baseline losses. |
| **Active Operational Shipments** | **24 shipments** | Tested multi-corridor active shipments seeded into production database across Nairobi, Nakuru, Kisumu, Eldoret, and Mombasa. |
| **Produce Batch Inventory** | **12 lots (~78,000 kg)** | High-value perishable produce lots actively tracked (Tomatoes, Avocados, Bananas, Mangoes, Maize, Beans, Potatoes, Kale). |
| **Regional Pricing Intelligence** | **90 market pairs** | 9 crop categories dynamically priced across 10 East African wholesale destination hubs with regional scarcity multipliers. |
| **Backend Test Coverage** | **38 / 38 passed (100%)** | Comprehensive automated test suite covering auth, produce batches, shipments, ML routes, and database models. |
| **Frontend Production Build** | **13 routes compiled** | Production Next.js 16 SSR & Static pages generated cleanly with 0 TypeScript and 0 ESLint errors. |
| **Audit PDF Generation** | **< 2.0 seconds** | High-speed executive compliance and dispatcher SOP report compilation powered by ReportLab. |

---

## 4. Mathematical & Algorithmic Formulations

### 4.1 Spoilage Friction Score Formulation
When routing trucks in transit, standard shortest-path algorithms (minimizing purely distance or time) fail because produce is actively degrading with every hour of heat exposure. Fresh Supplies implements a **spoilage-aware friction score** across the transit network graph $G = (V, E)$:

$$\text{Friction} = w_{\text{time}} \cdot \left(\frac{\Delta t}{24}\right) + w_{\text{spoilage}} \cdot \left(\frac{R_{\text{spoil}}}{100} + \max\left(0, \frac{T - 30}{10}\right)\right) + w_{\text{cost}} \cdot \left(\frac{d}{500}\right)$$

Where:
- $\Delta t$: Estimated transit time in hours.
- $R_{\text{spoil}}$: ML-predicted spoilage risk percentage ($0 \le R_{\text{spoil}} \le 100$).
- $T$: Current compartment temperature in Celsius (°C), with a steep non-linear penalty applied when temperatures exceed 30°C.
- $d$: Great-circle Haversine road distance in kilometers.
- Default calibrating weights: $w_{\text{time}} = 0.35$, $w_{\text{spoilage}} = 0.45$, $w_{\text{cost}} = 0.20$ (spoilage penalty is the dominant factor).

### 4.2 Economic Revenue Retention Formulation
For any alternative wholesale market destination $m \in M$, the expected gross revenue retained by the farmer or cooperative is defined as:

$$\text{Revenue}_{\text{retained}}(m) = Q \times P_m \times \left(1 - \frac{S(t_m)}{100}\right)$$

Where:
- $Q$: Produce shipment net quantity in kilograms (kg).
- $P_m$: Prevailing wholesale spot price per kilogram at destination market $m$ (KES/kg).
- $S(t_m)$: Projected cumulative spoilage percentage at arrival time $t_m$, compounding at an empirical degradation decay rate:
  $$S(t_m) = S_{\text{current}} + \alpha_{\text{crop}} \cdot \Delta t_m$$
  where $\alpha_{\text{crop}}$ represents the commodity-specific perishability coefficient (e.g., Tomatoes = $12.0$, Bananas = $11.0$, Mangoes = $10.5$, Potatoes = $6.0$).

---

## 5. System Architecture & Tech Stack

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT APPLICATIONS                               |
|                                                                                   |
|   +--------------------------+  +--------------------------+  +-----------------+ |
|   |  Next.js 16 Web Portal   |  |  Streamlit FreshOps UI   |  | Driver / SMS    | |
|   |  Tailwind, React 19,     |  |  Plotly, Interactive     |  | Offline Action  | |
|   |  Role-Based Analytics    |  |  What-If Diversion Maps  |  | Emergency Text  | |
|   +------------+-------------+  +------------+-------------+  +--------+--------+ |
+----------------|-----------------------------|-------------------------|----------+
                 |                             |                         |
                 | REST API / JSON             | Direct Pipeline Call    | Webhook
                 v                             v                         v
+-----------------------------------------------------------------------------------+
|                             CORE ENGINE LAYER (FastAPI)                           |
|                                                                                   |
|  +---------------------+ +----------------------+ +-----------------------------+ |
|  | Authentication &    | | Produce Batch &      | | ML Spoilage & Routing       | |
|  | RBAC Security       | | Shipment Controllers | | Endpoints                   | |
|  | JWT, bcrypt, CORS   | | CRUD, State Machine  | | /predict-spoilage           | |
|  |                     | | Active Monitoring    | | /recommend-market           | |
|  +----------+----------+ +----------+-----------+ +--------------+--------------+ |
|             |                       |                            |                |
|             +-----------------------+----------------------------+                |
|                                     |                                             |
|                                     v                                             |
|                      SQLAlchemy 2.0 ORM Database Layer                            |
+-------------------------------------+---------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------------+
|                                DATA & INFRASTRUCTURE                              |
|                                                                                   |
|  +-----------------------------+  +---------------------------------------------+ |
|  | PostgreSQL 16 Relational DB |  | Scikit-learn, XGBoost, NetworkX Pipeline    | |
|  | 24 Shipments, 12 Batches,   |  | Trained on 10,000+ telemetry rows           | |
|  | Historical telemetry logs   |  | Embedded SMOTE, SHAP explainability         | |
|  +-----------------------------+  +---------------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

### Technology Breakdown:
- **Backend Service:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 ORM, Uvicorn ASGI server.
- **Database:** PostgreSQL 16 hosted via Docker container (`freshroute-postgres`), with Alembic migration versioning.
- **Frontend Portal:** Next.js 16 (App Router + Turbopack), React 19, TypeScript, Tailwind CSS, Lucide Icons.
- **Machine Learning & Graph Analytics:** Scikit-learn, XGBoost, Imbalanced-learn (SMOTE), NetworkX, SHAP, Joblib.
- **Operations & Reporting:** Streamlit operational room (`ops_tool`), Plotly interactive geospatial routing maps, ReportLab executive PDF generator, and Next.js live CSV export engine.
- **Containerization:** Multi-service Docker Compose architecture (`docker-compose.yml`) supporting isolated database, backend, frontend, and automated migration services.

---

## 6. Supported Wholesale Markets & Crop Intelligence

### 6.1 The 10 Tracked Regional Wholesale Hubs
FreshRoute actively benchmarks and routes to 10 principal agricultural markets across Kenya:

| Hub Code | Market Hub Name | Coordinates (Lat, Lon) | Agricultural Region | Scarcity Index |
| :--- | :--- | :--- | :--- | :--- |
| `MKT_NAI` | **Nairobi Gikomba Market** | -1.2864, 36.8300 | Nairobi | 1.12x (Premium) |
| `MKT_MOM` | **Mombasa Kongowea Market** | -4.0435, 39.6682 | Coastal | 1.08x (High Demand) |
| `MKT_THK` | **Thika Wholesale Market** | -1.0333, 37.0693 | Central / Kiambu | 1.05x |
| `MKT_NKU` | **Nakuru Wakulima Market** | -0.3031, 36.0800 | Rift Valley | 1.02x |
| `MKT_KIS` | **Kisumu Open Air Market** | -0.0917, 34.7680 | Lake Basin | 1.00x (Baseline) |
| `MKT_NKR` | **Naivasha Market** | -0.7172, 36.4312 | Rift Valley | 1.00x |
| `MKT_ELD` | **Eldoret Central Market** | 0.5143, 35.2698 | North Rift | 0.98x |
| `MKT_KSM` | **Kakamega Municipal Market** | 0.2833, 34.7500 | Western | 0.97x |
| `MKT_BOM` | **Bomet Market** | -0.7800, 35.3400 | South Rift | 0.96x |
| `MKT_MER` | **Meru Wholesale Market** | 0.0500, 37.6500 | Eastern / Mount Kenya | 0.95x |

### 6.2 Perishable Crop Profiles & Base Economics
Nine foundational food crops are continuously monitored with calibrated baseline wholesale prices and frailty indices:

| Commodity | Food Class | Base Wholesale Price (KES/kg) | Perishability Frailty Index | Primary Transit Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Tomatoes** | FOOD | 90.00 | 12.0 (Highest) | Rapid softening, skin rupture above 24°C |
| **Bananas** | FOOD | 60.00 | 11.0 (Very High) | Accelerating ethylene release and overripening |
| **Mangoes** | FOOD | 85.00 | 10.5 (Very High) | Thermal blistering, flesh breakdown |
| **Kale (Sukumawiki)** | FOOD | 40.00 | 10.0 (High) | Moisture desiccation, rapid wilting |
| **Avocados** | FOOD | 120.00 | 9.0 (High) | Premature ripening, high margin loss |
| **Beans** | FOOD | 110.00 | 8.5 (Moderate) | Heat humidity mold risk |
| **Onions** | FOOD | 70.00 | 8.0 (Moderate) | Sprouting and fungal neck rot |
| **Maize** | FOOD | 45.00 | 7.0 (Moderate-Low) | Mold accumulation under moisture |
| **Potatoes** | FOOD | 55.00 | 6.0 (Low-Moderate) | Greening, soft rotting in excessive heat |

---

## 7. End-to-End Operational Workflow

```
[ STEP 1: Harvest & Batch Ingestion ]
    Farmers or cooperative managers register produce lots via /api/v1/produce.
    Details recorded: crop type, quantity (kg), harvest timestamp, field location.
           |
           v
[ STEP 2: Dispatch & Active Transit Initialization ]
    Shipment created with carrier, driver phone, assigned vehicle, route start, and target market.
    Initial status: PENDING -> IN_TRANSIT.
           |
           v
[ STEP 3: Automated Telemetry Ingestion & Spoilage Watchdog ]
    Periodic temperature (°C), pressure (PSI), transit hours, and coordinates streamed to backend.
    FastAPI calls /predict-spoilage.
           |
           v
[ STEP 4: Risk Evaluation & Automated Rerouting Trigger ]
    IF Spoilage < 15%:
        -> Shipment maintains current transit route. Status remains FRESH.
    IF Spoilage >= 15%:
        -> System alerts dispatcher.
        -> /recommend-market computes alternative destinations ranked by retained revenue.
        -> Driver receives SMS/App instruction to divert to selected market hub.
           |
           v
[ STEP 5: Destination Arrival & Quality Verification ]
    Truck arrives at receiving hub. Off-taker performs receiving inspection.
    Shipment transitions to DELIVERED. Final salvage payout recorded.
           |
           v
[ STEP 6: Executive Audit & Analytical Reporting ]
    Cooperative management downloads executive audit reports:
    - CSV raw records via /dashboard/reports.
    - PDF Compliance & Action Reports via FreshOps ReportLab engine.
```

---

## 8. Verification & Quality Assurance Results

The platform has undergone rigorous unit, integration, and UI verification:

1. **Automated Backend Testing:**
   - **Status:** 38 / 38 Pytest assertions passing (`backend/tests`).
   - **Suites:** `test_auth.py`, `test_main.py`, `test_produce.py`, `test_shipments.py`, `test_models.py`.
2. **Frontend Type Safety & Linting:**
   - **TypeScript Compiler (`tsc --noEmit`):** Clean compilation, 0 type errors across all app routes and components.
   - **ESLint Validation:** 0 warnings or lint errors across client codebase.
   - **Next.js Production Build:** 13 pages compiled successfully with zero build discrepancies.
3. **Database Integrity & Live Seed:**
   - Validated against running PostgreSQL 16 instance with 24 multi-corridor shipments, 12 produce batches, and live coordinate mappings across Kenya.

---

## 9. Team Acknowledgments & Core Contributors

The **Fresh Supplies (FreshRoute AI)** platform was developed through dedicated engineering, agricultural research, and systems integration. Special recognition goes to the core project leadership:

* **[Umar Ndungo](https://github.com/umarndungo)** — Architecture, Data Engineering & Agricultural Systems Strategy
* **[wochuna.](https://github.com/wochuna)** — Machine Learning Pipelines, Spoilage Modeling & Algorithmic Optimization
* **[Kelvin Moruri](https://github.com/kelvinMORURI)** — Full-Stack Systems Integration, Backend Architecture, Dashboard Engineering & Verification

---

## 10. Conclusion & Future Roadmap

Fresh Supplies demonstrates how practical artificial intelligence and edge telemetry can solve one of the developing world's most critical economic and humanitarian challenges: post-harvest food waste. By shifting from reactive write-offs to proactive algorithmic arbitrage, the platform protects agricultural livelihood, stabilizes urban food supply chains, and ensures that more nutritious food reaches African dinner tables.

Future extensions include:
- Integration of USSD fallback for non-smartphone truck drivers in rural low-signal areas.
- Solar-powered IoT hardware logger blueprints using ESP32 and BLE temperature probes.
- Dynamic market supply balancing using cooperative-to-market federated matching.


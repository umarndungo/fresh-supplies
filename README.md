# Fresh Supplies

Reduce post-harvest losses in Sub-Saharan Africa through data-driven spoilage prediction, risk segmentation, and spoilage-aware route and market optimization.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL 16 |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui, TanStack Query |
| ML/Data Engine | Python, scikit-learn, XGBoost, SHAP, Pandas, NetworkX |
| Mobile API | FastAPI (`/mobile/*` routes), OTP auth, offline-sync staging table |
| Infra | Docker Compose, Oracle Cloud Free Tier (target) |

## Project Structure

```
fresh-supplies/
├── backend/                  # FastAPI REST API
│   ├── app/
│   │   ├── core/             # Config, security, JWT, i18n, exceptions
│   │   ├── domain/           # Entities, enums, abstract repositories
│   │   ├── infrastructure/   # SQLAlchemy models & repository implementations
│   │   ├── application/      # Services, Pydantic schemas, ML inference
│   │   └── api/
│   │       ├── routes/       # auth, shipments, produce, ml, mobile_*
│   │       ├── deps.py       # Dependency injection
│   │       └── router.py     # Route registration
│   ├── alembic/              # Database migrations
│   └── tests/                # pytest + httpx
├── src/                      # Next.js web frontend
├── post_harvest_data_engine/ # ML training, ETL, data pipeline
├── docs/                     # Developer handoff docs, API contracts
├── docker-compose.yml        # PostgreSQL 16
└── PROJECT_PLAN.md           # 5-phase project roadmap
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 16 (or Docker)

### 1. Database

```bash
docker compose up -d          # Starts PostgreSQL 16 on localhost:5432
```

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Edit JWT_SECRET_KEY and DATABASE_URL
alembic upgrade head           # Apply migrations
uvicorn app.main:app --reload  # http://localhost:8000
```

### 3. Frontend

```bash
npm install
npm run dev                    # http://localhost:3000
```

### 4. Tests

```bash
cd backend
python -m pytest tests/ -v
```

## Backend API

All routes are mounted under `/api/v1`. Responses use the `{"data": ...}` wrapper.

### Auth (`/auth`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | No | Create account (email/password) |
| `POST` | `/auth/login` | No | Login (email/password) |
| `POST` | `/auth/refresh` | Cookie | Refresh access token |
| `POST` | `/auth/logout` | No | Clear refresh cookie |
| `GET` | `/auth/me` | Bearer | Current user profile |

### Shipments (`/shipments`)

| Method | Path | Auth | Roles |
|---|---|---|---|
| `GET` | `/shipments` | Bearer | Any |
| `POST` | `/shipments` | Bearer | Admin, Logistics Manager |
| `GET` | `/shipments/{id}` | Bearer | Any |
| `PATCH` | `/shipments/{id}` | Bearer | Admin, Logistics Manager |
| `DELETE` | `/shipments/{id}` | Bearer | Admin, Logistics Manager |

### Produce (`/produce`)

| Method | Path | Auth | Roles |
|---|---|---|---|
| `GET` | `/produce` | Bearer | Any |
| `POST` | `/produce` | Bearer | Admin, Farmer Cooperative |
| `GET` | `/produce/{id}` | Bearer | Any |
| `PATCH` | `/produce/{id}` | Bearer | Admin, Farmer Cooperative |
| `DELETE` | `/produce/{id}` | Bearer | Admin, Farmer Cooperative |

### ML (`/ml`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/ml/predict-spoilage` | Bearer | Spoilage risk + probability |
| `POST` | `/ml/recommend-market` | Bearer | Ranked market destinations |

### Mobile API (`/mobile`)

Offline-first endpoints for the field mobile app (Flutter). Uses phone+OTP auth, idempotent batch sync, and simplified payloads.

#### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/mobile/auth/otp/request` | No | Send OTP to phone number |
| `POST` | `/mobile/auth/otp/verify` | No | Verify OTP, get JWT + refresh token in body |
| `POST` | `/mobile/auth/refresh` | Body | Refresh tokens (reads from body, not cookie) |
| `POST` | `/mobile/auth/complete-profile` | Bearer | Set name, account type (Cooperative/Individual) |

#### Shipments

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/mobile/shipments/sync` | Bearer | Batch idempotent upsert (staging table) |
| `POST` | `/mobile/shipments/photo-upload` | Bearer | Multipart photo upload (local disk) |
| `GET` | `/mobile/shipments/sync-status` | Bearer | Delta pull of server-side changes |
| `GET` | `/mobile/shipments/{id}/recommendation` | Bearer | Simplified risk tier + top market |

#### Driver

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/mobile/driver/manifest` | Bearer | Grouped pickup stops for date |
| `POST` | `/mobile/driver/stops/{id}/confirm` | Bearer | Confirm pickup (SCHEDULED -> IN_TRANSIT) |

#### Devices

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/mobile/devices/register` | Bearer | Register FCM/APNs push token |

## Architecture

The backend follows **Clean Architecture**:

```
Route -> Service -> Repository -> ORM
  |        |            |
  HTTP    Business     SQLAlchemy
  layer   logic        async
```

- **Domain layer** (`domain/`): frozen dataclasses and abstract repository ABCs. No framework dependencies.
- **Infrastructure** (`infrastructure/`): SQLAlchemy 2.0 async models and repository implementations.
- **Application** (`application/`): Pydantic schemas, service classes with business logic and role enforcement.
- **API** (`api/`): FastAPI route handlers, dependency injection via `deps.py`.
- **Mobile API** (`api/routes/mobile_*`): Separate route modules under `/mobile` with phone auth, offline sync, and simplified payloads. Writes go to a `shipment_sync_staging` table, reconciled into `shipments` by a background job.

### User Roles

| Role | Permissions |
|---|---|
| `ADMINISTRATOR` | Full access |
| `LOGISTICS_MANAGER` | Manage shipments |
| `FARMER_COOPERATIVE` | Manage produce, mobile capture |
| `MARKET_ANALYST` | Read-only, ML endpoints |

### Account Types (Mobile)

| Type | Ownership |
|---|---|
| `COOPERATIVE` | Produce/shipments owned by `cooperative_id`; submitter tracked separately |
| `INDIVIDUAL` | Produce/shipments owned directly by `user_id` |

## Data Engine

Located in `post_harvest_data_engine/`. Handles:

- **ETL**: FAOSTAT agricultural data, CHIRTS/CHIRPS climate data, synthetic logistics telemetry, market pricing.
- **Feature engineering**: Thermal heat exposure, temperature rolling stats, crop susceptibility, distance-to-market.
- **Model training**: Random Forest / XGBoost classifiers with SMOTE, cost-optimized threshold selection, SHAP explainability.
- **Risk segmentation**: K-Means clustering into Fresh / At-Risk / Critical tiers.
- **Route optimization**: NetworkX graph with spoilage-aware friction scoring and Pareto-front market recommendation.

Trained model artifacts are loaded at backend startup for real-time inference via `/ml/predict-spoilage` and `/ml/recommend-market`.

## Environment Variables

### Backend (`backend/.env`)

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/freshroute
JWT_SECRET_KEY=<random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_ORIGIN=http://localhost:3000
```

### Frontend (`src/.env.local`)

```env
NEXT_PUBLIC_APP_NAME=Fresh Supplies
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Docs

- `docs/backend_developer_handoff.md` — Backend setup and conventions
- `docs/frontend_developer_handoff.md` — Frontend setup and conventions
- `docs/mobile_ussd_developer_handoff.md` — Mobile/USSD architecture
- `docs/freshroute-mobile-api-contract.md` — Mobile API contract v0.2
- `docs/data_engine_developer_handoff.md` — ML/data engine guide
- `docs/deployment_devops_notes.md` — Deployment notes

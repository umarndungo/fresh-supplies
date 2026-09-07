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
├── db/                       # PostgreSQL provisioning (init/provision.sh + bootstrap.sh wrapper)
├── backend/Dockerfile        # FastAPI dev image (uvicorn --reload)
├── Dockerfile                # Next.js dev image (next dev)
├── docker-compose.yml        # Full stack: postgres, backend, frontend + one-shot DB tasks
└── PROJECT_PLAN.md           # 5-phase project roadmap
```

## Getting Started

Everything runs in Docker: Postgres, the FastAPI backend, and the Next.js
frontend, plus containerized one-shot tasks for DB provisioning and migrations.

### Prerequisites

- Docker + Docker Compose (v2) — nothing else is required at runtime
- Python 3.12+ / Node 22+ only if you want to run backend/frontend on the host
  instead of in containers

### 1. Environment (private, gitignored)

Two private env files. Secrets never leave these:

```bash
cp .env.example .env          # edit DB_NAME, DB_USER, DB_PASS and NEXT_PUBLIC_* as you like
cd backend
cp .env.example .env          # edit JWT_SECRET_KEY; DATABASE_URL uses the same DB_* user/db
cd ..
```

Defaults: `freshroute` / `freshrouteadmin` / `freshroute@2120`.

### 2. Full stack up

```bash
docker compose up -d          # postgres :5432, backend :8000, frontend :3000
```

- On a **fresh** postgres volume, `db/init/provision.sh` auto-creates the `.env`
  DB role and makes it owner of the database.
- Backend source (`backend/`) and frontend source (repo root, `src/`) are
  bind-mounted with live reload — edit files and the running app picks them up.
- Model artifacts are mounted read-only from
  `post_harvest_data_engine/data/processed/food/`.

### 3. Database tasks (containerized one-shots)

```bash
docker compose run --rm db-migrate      # alembic upgrade head (as the app user)
./db/bootstrap.sh                       # one-time, for EXISTING volumes that predate provision.sh
                                        # (== docker compose run --rm db-bootstrap)
```

Both read `DB_NAME` / `DB_USER` / `DB_PASS` from your `.env` — nothing is
hardcoded. Idempotent; safe to re-run.

### 4. Tests (optional, on the host)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
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

### Database / Docker (`./.env`)

```env
DB_NAME=freshroute
DB_USER=freshrouteadmin
DB_PASS=freshroute@2120
```

Copied from `.env.example` and edited to your liking — gitignored, so these stay
private. Consumed by `docker-compose.yml` (postgres provisioning + one-shot
tasks), `db/init/provision.sh`, and `backend/entrypoint.sh`.

### Backend (`backend/.env`)

```env
DATABASE_URL=postgresql+asyncpg://freshrouteadmin:freshroute%402120@localhost:5432/freshroute
JWT_SECRET_KEY=<random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_ORIGIN=http://localhost:3000
```

`DATABASE_URL` user/password/db must match the `DB_USER`/`DB_PASS`/`DB_NAME`
values above (a literal `@` in the password is URL-encoded as `%40`), and must
not be the `postgres` superuser. In containers the URL is derived from `DB_*`
(host `postgres`) by `backend/entrypoint.sh`, so keep the two in sync only if
you also run the backend on the host.

### Frontend (root `.env` / `src/.env.local`)

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

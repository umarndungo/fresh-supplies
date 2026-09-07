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

You can run Fresh Supplies in either of two ways:
1. **Option A: Full Docker Mode** — Runs PostgreSQL, FastAPI backend, and Next.js frontend in Docker containers.
2. **Option B: Local Development Mode** — Runs PostgreSQL in Docker, while running the FastAPI backend and Next.js frontend natively on your host machine for rapid iterative development.

---

### Prerequisites

- **Docker Desktop** (running with Docker Compose v2)
- For local host execution:
  - **Python 3.10+ / 3.12+**
  - **Node.js 20+ / 22+** and **npm**

---

### Option A: Full Docker Mode (All Containers)

#### 1. Setup Environment Files
```bash
# In project root:
cp .env.example .env

# In backend directory:
cd backend
cp .env.example .env
cd ..
```
*Defaults in `.env.example` configure `freshroute` database credentials and dev settings.*

#### 2. Start All Services
```bash
docker compose up -d
```
This spins up:
- **PostgreSQL 16**: Port `5432`
- **FastAPI Backend**: Port `8000` (live reload enabled)
- **Next.js Frontend**: Port `3000` (live reload enabled)

#### 3. Run Database Migrations
On first boot, apply the database schema migrations via the one-shot container:
```bash
docker compose run --rm db-migrate
```

---

### Option B: Local Development Mode (Recommended for Host Debugging)

In this mode, PostgreSQL runs in Docker, while the backend and frontend run in your terminals.

#### Step 1: Start PostgreSQL via Docker
Ensure Docker Desktop is open and running, then execute from the project root:
```powershell
# Start only the database container in background
docker compose up -d postgres
```

#### Step 2: Set Up and Run the Backend (FastAPI)

1. Navigate to `backend` and create your `.env` file:
   ```powershell
   cd backend
   cp .env.example .env
   ```
   *Ensure `JWT_SECRET_KEY` in `backend/.env` is populated with a random secret string.*

2. Create and activate a Python virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS (Bash):**
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Step 3: Set Up and Run the Frontend (Next.js)

1. In a new terminal, navigate to the project root:
   ```bash
   # If you have a root .env.example:
   cp .env.example .env.local
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

---

### Verification & URLs

Once running, access the following endpoints:

| Service | URL | Description |
|---|---|---|
| **Web Frontend** | [http://localhost:3000](http://localhost:3000) | Next.js App (Landing, Register, Login, Dashboard) |
| **API Health Check** | [http://localhost:8000/health](http://localhost:8000/health) | Verifies FastAPI is alive (`{"status":"ok"}`) |
| **Swagger Interactive Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive API documentation |
| **ReDoc API Spec** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Alternative API documentation |

---

### Troubleshooting & Common Pitfalls

#### 1. "Failed to connect to the docker API"
- **Cause**: Docker Desktop is not running or still starting up.
- **Solution**: Open Docker Desktop from the Start Menu / Applications and wait until the Docker whale icon in the taskbar shows "Engine running".

#### 2. Port 8000 or 5432 Already in Use
- **Cause**: An old container from another project (or an orphaned process) is bound to the port.
- **Solution**:
  - Check running containers: `docker ps`
  - Stop any conflicting container: `docker stop <container_name_or_id>`
  - If a local service is using port 5432 or 8000, stop it before starting Fresh Supplies.

#### 3. Frontend Displays "Network Error" / "CORS policy" on Register/Login
- **Cause**: The FastAPI backend threw an unhandled exception (typically `500 Internal Server Error` because PostgreSQL is offline or refusing connections on port 5432).
- **Solution**:
  - Verify PostgreSQL is running: `docker compose ps` (should show `freshroute-postgres` as healthy).
  - Verify database migrations have run: `alembic upgrade head`.
  - Verify `DATABASE_URL` in `backend/.env` matches your postgres credentials.

#### 4. Windows PowerShell Script Execution Policy (`Activate.ps1 cannot be loaded`)
- **Cause**: PowerShell restricts executing scripts by default.
- **Solution**: Run this in your current PowerShell session:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
  Then re-run `.\.venv\Scripts\Activate.ps1`.

#### 5. Resetting Database Volume
To start with a completely fresh, empty PostgreSQL database:
```bash
docker compose down -v
docker compose up -d postgres
cd backend
alembic upgrade head
```

---

### Running Tests

To run backend tests on the host:
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

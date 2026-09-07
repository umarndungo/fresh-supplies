# Fresh Supplies — Backend API

FastAPI REST API powering Fresh Supplies. Implements clean architecture (Domain, Infrastructure, Application, and API layers) with SQLAlchemy 2.0 (async), PostgreSQL 16, Alembic migrations, and JWT authentication.

---

## 1. Prerequisites

- **Python 3.10+ / 3.12+**
- **Docker Desktop** (for running PostgreSQL 16)

---

## 2. Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Open `.env` and verify the values:
```env
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/freshroute
JWT_SECRET_KEY=your-random-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_ORIGIN=http://localhost:3000
REFRESH_COOKIE_NAME=frs_refresh_token
COOKIE_SECURE=false
```

---

## 3. Start PostgreSQL Database

From the project root:
```bash
docker compose up -d postgres
```

Verify that the container is healthy:
```bash
docker compose ps
```

---

## 4. Virtual Environment & Dependencies

From the `backend/` directory:

### Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

*(If script execution is blocked on PowerShell, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Linux / macOS (Bash):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 5. Apply Database Migrations

With the virtual environment activated, run:
```bash
alembic upgrade head
```

To create a new migration after editing SQLAlchemy models:
```bash
alembic revision --autogenerate -m "describe your changes"
alembic upgrade head
```

---

## 6. Start the Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 7. Interactive Documentation & Health Check

Once started, test the server:
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Swagger Interactive API**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Spec**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 8. Running Automated Tests

```bash
python -m pytest tests/ -v
```

---

## 9. Common Issues

- **ConnectionRefusedError / WinError 1225 on port 5432**:
  PostgreSQL is not running. Check Docker Desktop is running, and run `docker compose up -d postgres`.
- **Address already in use on port 8000**:
  Another process or Docker container is bound to port 8000. Check with `docker ps` or stop the conflicting process.
- **Frontend shows "Network Error" / "CORS policy"**:
  FastAPI returns 500 when it cannot reach PostgreSQL. Start Postgres and run `alembic upgrade head`.


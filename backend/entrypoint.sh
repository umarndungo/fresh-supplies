#!/usr/bin/env bash
#
# Container entrypoint for the backend image.
#
# Inside the compose network the DB host is the `postgres` service, not
# localhost. If the .env DB_* variables are present, derive DATABASE_URL from
# them (overriding any localhost URL injected via backend/.env's env_file or
# pydantic-settings .env file). On the host nothing changes — run uvicorn from
# the venv as before.
#
# The password is URL-encoded for the DSN (% -> %25 first, then @ -> %40).

set -euo pipefail

if [[ -n "${DB_USER:-}" && -n "${DB_PASS:-}" && -n "${DB_NAME:-}" ]]; then
  ENC_PASS="${DB_PASS//%/%25}"
  ENC_PASS="${ENC_PASS//@/%40}"
  DATABASE_URL="postgresql+asyncpg://${DB_USER}:${ENC_PASS}@${DB_HOST:-postgres}:${DB_PORT:-5432}/${DB_NAME}"
  export DATABASE_URL
  echo "entrypoint: using DATABASE_URL host '${DB_HOST:-postgres}' (user '${DB_USER}')"
fi

exec "$@"
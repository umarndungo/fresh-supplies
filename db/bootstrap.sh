#!/usr/bin/env bash
#
# One-time local PostgreSQL bootstrap.
#
# Logs into the running postgres container as the superuser and provisions the
# application role + database privileges/ownership using the DB_NAME / DB_USER /
# DB_PASS variables from your private .env (see .env.example). The values are
# read from .env so they stay secret and are easy to change; the same variables
# drive docker-compose (POSTGRES_DB/POSTGRES_APP_*) on fresh volumes.
#
# Usage:
#   cp .env.example .env     # first time, then edit DB_NAME/DB_USER/DB_PASS
#   ./db/bootstrap.sh        # existing volumes that predate db/init
#
# Precedence: exported DB_NAME/DB_USER/DB_PASS > .env > backend/.env
# DATABASE_URL-derived > built-in defaults.
#
# Safe to run repeatedly (idempotent).

set -euo pipefail

ENV_FILE="${ENV_FILE:-$(dirname "$0")/.env}"
BE_ENV_FILE="${BE_ENV_FILE:-$(dirname "$0")/../backend/.env}"
CONTAINER="${CONTAINER:-freshroute-postgres}"

DEFAULT_URL="postgresql+asyncpg://freshrouteadmin:freshroute%402120@localhost:5432/freshroute"

# --- Primary source: DB_* variables from .env ---
if [[ -f "$ENV_FILE" ]]; then
  while IFS='=' read -r KEY VAL; do
    case "$KEY" in
      DB_NAME|DB_USER|DB_PASS)
        if [[ -z "${!KEY:-}" ]]; then
          declare "$KEY=$VAL"
        fi
        ;;
    esac
  done < <(grep -E '^(DB_NAME|DB_USER|DB_PASS)=' "$ENV_FILE")
fi

# --- Fallback: derive any missing ones from DATABASE_URL (backend/.env > default) ---
DATABASE_URL="${DATABASE_URL:-$DEFAULT_URL}"
if [[ -f "$BE_ENV_FILE" ]]; then
  BE_URL="$(grep -E '^DATABASE_URL=' "$BE_ENV_FILE" | head -n 1 | cut -d= -f2- | tr -d '"')"
  [[ -n "$BE_URL" ]] && DATABASE_URL="$BE_URL"
fi
no_scheme="${DATABASE_URL#*://}"
creds="${no_scheme%@*}"
DB_NAME="${DB_NAME:-${no_scheme##*/}}"
DB_USER="${DB_USER:-${creds%%:*}}"
DB_PASS="${DB_PASS:-${creds#*:}}"
DB_PASS="${DB_PASS//%40/@}"               # URL-decode @ in the password

if [[ -z "$DB_USER" || -z "$DB_PASS" || -z "$DB_NAME" ]]; then
  echo "error: DB_NAME/DB_USER/DB_PASS are empty — set them in .env or DATABASE_URL" >&2
  exit 1
fi

# --- Warn if the running app config (backend/.env) no longer matches .env ---
if [[ -f "$BE_ENV_FILE" ]]; then
  BE_URL="$(grep -E '^DATABASE_URL=' "$BE_ENV_FILE" | head -n 1 | cut -d= -f2- | tr -d '"')"
  if [[ -n "$BE_URL" ]]; then
    BE_CREDS="${BE_URL#*://}"; BE_CREDS="${BE_CREDS%@*}"
    BE_DB="${BE_URL##*/}"
    if [[ "$BE_DB" != "$DB_NAME" || "${BE_CREDS%%:*}" != "$DB_USER" ]]; then
      echo "warning: backend/.env DATABASE_URL uses ${BE_CREDS%%:*}@.../${BE_DB}, but .env has ${DB_USER}@${DB_NAME}" >&2
      echo "warning: update backend/.env DATABASE_URL to match your .env DB_* values" >&2
    fi
  fi
fi

echo "Bootstrapping PostgreSQL app user '${DB_USER}' for database '${DB_NAME}' in container '${CONTAINER}'..."

docker exec -i "$CONTAINER" psql -U postgres -v ON_ERROR_STOP=1 <<EOSQL
-- Create the role if it does not exist yet.
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASS}';
  END IF;
END
\$\$;

-- Create the database if it does not exist yet (no-op when compose already created it).
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec

GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER};
EOSQL

echo "OK: PostgreSQL user '${DB_USER}' owns '${DB_NAME}' with all privileges."
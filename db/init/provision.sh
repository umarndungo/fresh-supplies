#!/usr/bin/env bash
#
# Provisions the application PostgreSQL role, database, privileges, and ownership.
# This is the single source of truth for the provisioning SQL. It is used two ways:
#
#   1. Fresh postgres volume: docker-compose.yml mounts this directory into
#      /docker-entrypoint-initdb.d, so it runs automatically at first
#      `docker compose up`. Values come from your private .env via compose
#      substitution (POSTGRES_DB <- DB_NAME, POSTGRES_APP_USER <- DB_USER,
#      POSTGRES_APP_PASSWORD <- DB_PASS), with built-in dev defaults.
#   2. Existing volume (one-shot): `docker compose run --rm db-bootstrap` runs this
#      script in a postgres:16-alpine client container, connecting over the compose
#      network (PGHOST=postgres, PGUSER/PGPASSWORD=postgres).
#
# Connect context differs per mode but both use the postgres superuser:
#   - init: local socket as POSTGRES_USER
#   - bootstrap: TCP via PGHOST/PGPORT/PGUSER/PGPASSWORD
#
# Safe to run repeatedly (idempotent) — role/db are created only if missing, the
# GRANT/OWNER statements are no-ops once they hold.

set -eu

# --- Connection (superuser) ---
PGUSER="${PGUSER:-${POSTGRES_USER:-postgres}}"

# --- App values to provision ---
DB_NAME="${DB_NAME:-${POSTGRES_DB:-freshroute}}"
APP_USER="${APP_USER:-${DB_USER:-${POSTGRES_APP_USER:-freshrouteadmin}}}"
APP_PASS="${APP_PASS:-${DB_PASS:-${POSTGRES_APP_PASSWORD:-freshroute@2120}}}"

# POSIX-safe: array-free psql invocation. PGHOST/PGPORT are empty during init
# (local socket) and set to the postgres service during the db-bootstrap one-shot.
psql -v ON_ERROR_STOP=1 --no-psqlrc --no-password --username "$PGUSER" \
  ${PGHOST:+-h "$PGHOST"} ${PGPORT:+-p "$PGPORT"} <<SQL
-- Create the application role if it does not exist yet.
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${APP_USER}') THEN
    CREATE ROLE ${APP_USER} WITH LOGIN PASSWORD '${APP_PASS}';
  END IF;
END
\$\$;

-- Create the database if it does not exist yet.
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${APP_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec

GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${APP_USER};
ALTER DATABASE ${DB_NAME} OWNER TO ${APP_USER};
SQL

echo "OK: PostgreSQL user '${APP_USER}' owns '${DB_NAME}' with all privileges."
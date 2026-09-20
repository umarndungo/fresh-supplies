#!/usr/bin/env bash
#
# Runs Alembic migrations (alembic upgrade head) against a running compose
# stack's database. Idempotent — safe to run any time, including when
# already at head. This is also what runs automatically on every
# `docker compose up` now (see db-migrate in docker-compose.yml /
# local-docker-compose.yml); this script is for re-running it on demand
# without restarting the stack (e.g. after adding a new migration file).
#
# Usage:
#   ./scripts/migrate.sh          # full Docker mode (docker-compose.yml)
#   ./scripts/migrate.sh local    # local-dev mode (local-docker-compose.yml)

set -euo pipefail
cd "$(dirname "$0")/.."

if [ "${1:-}" = "local" ]; then
  echo "Running migrations against the local-dev stack..."
  exec docker compose -f local-docker-compose.yml run --rm db-migrate
else
  echo "Running migrations against the full Docker stack..."
  exec docker compose run --rm db-migrate
fi

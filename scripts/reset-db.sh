#!/usr/bin/env bash
#
# DESTROYS the Postgres volume for a compose stack and brings it back up
# from scratch (fresh volume -> provision.sh auto-runs via
# docker-entrypoint-initdb.d -> db-migrate runs alembic upgrade head).
# Useful when local migration history has drifted or you just want a clean
# slate. This is destructive and asks for confirmation before doing anything.
#
# Usage:
#   ./scripts/reset-db.sh          # full Docker mode (docker-compose.yml)
#   ./scripts/reset-db.sh local    # local-dev mode (local-docker-compose.yml)

set -euo pipefail
cd "$(dirname "$0")/.."

if [ "${1:-}" = "local" ]; then
  COMPOSE=(docker compose -f local-docker-compose.yml)
  LABEL="local-dev"
else
  COMPOSE=(docker compose)
  LABEL="full Docker"
fi

echo "This will DELETE ALL DATA in the $LABEL stack's Postgres volume."
read -r -p "Type 'yes' to continue: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted — nothing was changed."
  exit 1
fi

"${COMPOSE[@]}" down -v
"${COMPOSE[@]}" up -d
echo "Done — fresh volume provisioned and migrated. Check status with:"
echo "  ${COMPOSE[*]} ps"

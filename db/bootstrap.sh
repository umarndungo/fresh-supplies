#!/usr/bin/env bash
#
# One-time PostgreSQL bootstrap for EXISTING volumes (volumes that predate
# db/init/provision.sh). Fresh volumes are provisioned automatically at first
# `docker compose up`; this runs the same script (`db/init/provision.sh`) inside
# a throwaway postgres client container against the postgres service.
#
# Reads DB_NAME / DB_USER / DB_PASS from your private .env (compose does the
# substitution), so nothing is hardcoded and nothing is shared.
#
#   ./db/bootstrap.sh                 # == docker compose run --rm db-bootstrap
#
# Safe to run repeatedly (idempotent).

set -euo pipefail

cd "$(dirname "$0")/.."
exec docker compose run --rm db-bootstrap
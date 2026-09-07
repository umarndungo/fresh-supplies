#!/bin/bash
#
# Runs automatically the FIRST time a postgres_data volume is initialized
# (mounted into /docker-entrypoint-initdb.d by docker-compose.yml). The
# superuser (POSTGRES_USER=postgres) creates the application role that
# backend/.env's DATABASE_URL references and makes it owner of the database.
#
# Values come from your private .env via docker-compose substitution:
#   POSTGRES_DB         <- DB_NAME
#   POSTGRES_APP_USER   <- DB_USER
#   POSTGRES_APP_PASSWORD <- DB_PASS
#
# Only applies to fresh volumes. Re-running `docker compose up` on an existing
# volume does NOT re-run this — for those, use ./db/bootstrap.sh.

set -euo pipefail

APP_USER="${POSTGRES_APP_USER:-freshrouteadmin}"
APP_PASSWORD="${POSTGRES_APP_PASSWORD:-freshroute@2120}"
DB_NAME="${POSTGRES_DB:-freshroute}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	DO \$\$
	BEGIN
	  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${APP_USER}') THEN
	    CREATE ROLE ${APP_USER} WITH LOGIN PASSWORD '${APP_PASSWORD}';
	  END IF;
	END
	\$\$;

	GRANT ALL PRIVILEGES ON DATABASE "${DB_NAME}" TO ${APP_USER};
	ALTER DATABASE "${DB_NAME}" OWNER TO ${APP_USER};
EOSQL
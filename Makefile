# Fresh Supplies — Docker convenience targets.
#
# Two modes, mirroring README.md:
#   - Full Docker mode   (docker-compose.yml)       : make up / down / ...
#   - Local dev mode     (local-docker-compose.yml) : make local-up / local-down / ...
#
# Both modes now auto-provision the DB and run `alembic upgrade head` on
# every `up` — via the db-bootstrap/db-migrate one-shot services, ordered
# with `depends_on: condition: service_completed_successfully` so backend
# never starts against an unmigrated database. New migration files need no
# manual step: just `make up` (or `make migrate` to re-run without a
# restart).

.PHONY: up down restart logs ps build migrate bootstrap reset-db \
        local-up local-down local-restart local-logs local-ps local-migrate \
        help

COMPOSE = docker compose
LOCAL_COMPOSE = docker compose -f local-docker-compose.yml

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

## --- Full Docker mode (postgres + backend + frontend + caddy) ---

up: ## Start the full stack (auto-provisions DB + runs migrations first)
	$(COMPOSE) up -d

down: ## Stop the full stack
	$(COMPOSE) down

restart: down up ## Restart the full stack

logs: ## Tail logs for all services
	$(COMPOSE) logs -f

ps: ## Show service status
	$(COMPOSE) ps

build: ## Rebuild images
	$(COMPOSE) build

migrate: ## Re-run alembic migrations against the running stack (no restart needed)
	./scripts/migrate.sh

bootstrap: ## Re-provision the app DB role/ownership on an existing volume
	$(COMPOSE) run --rm db-bootstrap

reset-db: ## DESTROY the postgres volume and re-provision + re-migrate from scratch
	./scripts/reset-db.sh

## --- Local dev mode (postgres in Docker; backend/frontend hot-reload in Docker) ---

local-up: ## Start the local-dev stack (auto-migrates first)
	$(LOCAL_COMPOSE) up -d

local-down: ## Stop the local-dev stack
	$(LOCAL_COMPOSE) down

local-restart: local-down local-up ## Restart the local-dev stack

local-logs: ## Tail logs for the local-dev stack
	$(LOCAL_COMPOSE) logs -f

local-ps: ## Show local-dev service status
	$(LOCAL_COMPOSE) ps

local-migrate: ## Re-run alembic migrations against the local-dev stack
	./scripts/migrate.sh local

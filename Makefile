.PHONY: all 

REPO_ROOT := $(abspath $(PWD))
export REPO_ROOT

APP_COMPOSE=platform/app/docker-compose.yml
APP_COMPOSE_DEV=platform/app/docker-compose.dev.yml
LANGFUSE_COMPOSE=platform/observability/docker-compose.langfuse.yml

langfuse-dev:
	docker compose \
		--env-file platform/observability/.env \
		--env-file platform/observability/.env.dev \
		-p langfuse-dev \
		-f $(LANGFUSE_COMPOSE) \
		up -d

langfuse-prod:
	docker compose \
		--env-file platform/observability/.env \
		-p langfuse-prod \
		-f $(LANGFUSE_COMPOSE) \
		up -d


app-dev:
	docker compose \
		--env-file platform/app/.env \
		--env-file platform/app/.env.dev \
		-p app-dev \
		-f $(APP_COMPOSE) \
		-f $(APP_COMPOSE_DEV) \
		up --build -d


app-prod:
	docker compose \
		--env-file platform/app/.env \
		-p app-prod \
		-f $(APP_COMPOSE) \
		up --build -d

local-run-dev:
	make langfuse-dev
	make app-dev

local-run-prod:
	make langfuse-prod
	make app-prod

# TODO: Adhoc way to ingest products into vectorstore
ingest-products-vectordb:
	python chatbot/scripts/ingest_product_data_into_vectorstore.py \
	--sqlite-db-path "ecom-backend/ecom_backend.db"


check-all:
	SKIP=no-commit-to-branch pre-commit run --all-files $(if $(FILE),$(FILE),)

check-lint:
	pre-commit run ruff --all-files $(if $(FILE),$(FILE),)

check-format:
	pre-commit run ruff-format --all-files $(if $(FILE),$(FILE),)

# Individual make target for each pre-commit hook
check-hook-%:
	pre-commit run --hook-stage manual $* $(if $(FILE),$(FILE),--all-files)



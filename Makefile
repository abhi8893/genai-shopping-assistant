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


# Pre-commit targets with conditional FILE handling
check-all:
	@if [ -n "$(FILE)" ]; then \
		git ls-files -- $(FILE) | xargs pre-commit run --files; \
	else \
		pre-commit run --all-files; \
	fi

check-lint:
	@if [ -n "$(FILE)" ]; then \
		git ls-files -- $(FILE) | xargs pre-commit run ruff --files; \
	else \
		pre-commit run ruff --all-files; \
	fi

check-format:
	@if [ -n "$(FILE)" ]; then \
		git ls-files -- $(FILE) | xargs pre-commit run ruff-format --files; \
	else \
		pre-commit run ruff-format --all-files; \
	fi

check-secrets:
	@if [ -n "$(FILE)" ]; then \
		git ls-files -- $(FILE) | xargs pre-commit run gitleaks --files; \
	else \
		pre-commit run gitleaks --all-files; \
	fi

# Individual make target for each pre-commit hook
check-hook-%:
	@if [ -n "$(FILE)" ]; then \
		git ls-files -- $(FILE) | xargs pre-commit run --hook-stage manual $* --files; \
	else \
		pre-commit run --hook-stage manual $* --all-files; \
	fi

# TODO: Refine draw repo tree target
draw-repo-tree:
	tree -I "__pycache__|*.pyc|*.pyo|*.pyd|*.py,cover|.pytest_cache|.tox|.eggs|*.egg-info|.mypy_cache|.coverage|htmlcov|.pytest_cache|.venv|venv|env|ENV|.git|.github|.vscode|.idea|.DS_Store" -L 2

remove-dangling-images:
	docker images -f "dangling=true" -q | xargs -r docker rmi


# ========================================
# Virtual Environment Management
# ========================================

.PHONY: venv-create
venv-create:
ifndef COMPONENT
	$(error COMPONENT is required. Usage: make venv-create COMPONENT=packages/shopping-assistant [GROUP=dev|prod])
endif
	@python3 scripts/create_venv.py --repo-root $(REPO_ROOT) --component $(COMPONENT) --group $(if $(GROUP),$(GROUP),prod)

# Component-specific shortcuts
.PHONY: venv-package-dev venv-package-prod
venv-package-dev:
	@$(MAKE) venv-create COMPONENT=packages/shopping-assistant GROUP=dev

venv-package-prod:
	@$(MAKE) venv-create COMPONENT=packages/shopping-assistant GROUP=prod

.PHONY: venv-service-assistant-dev venv-service-assistant-prod
venv-service-assistant-dev:
	@$(MAKE) venv-create COMPONENT=services/shopping-assistant GROUP=dev

venv-service-assistant-prod:
	@$(MAKE) venv-create COMPONENT=services/shopping-assistant GROUP=prod

.PHONY: venv-service-ecom-dev venv-service-ecom-prod
venv-service-ecom-dev:
	@$(MAKE) venv-create COMPONENT=services/ecom-backend GROUP=dev

venv-service-ecom-prod:
	@$(MAKE) venv-create COMPONENT=services/ecom-backend GROUP=prod

.PHONY: venv-clean
venv-clean:
ifndef COMPONENT
	$(error COMPONENT is required. Usage: make venv-clean COMPONENT=packages/shopping-assistant)
endif
	@python3 scripts/clean_venv.py --repo-root $(REPO_ROOT) --component $(COMPONENT)

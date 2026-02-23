.PHONY: all venv-switch-all


REPO_ROOT := $(abspath $(PWD))
export DOCKER_BUILDKIT=1
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


# Example usage: make app-dev SERVICES=shopping-assistant ecom-backend
# $(if $(SERVICES),up --build -d --scale $(SERVICES)=0,$(if $(BUILD),build,$(if $(UP),up -d --build,$(error Please specify either BUILD, UP or SERVICES))))

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
	@echo ""
	@echo "----------------------------------------"
	@$(MAKE) -s venv-get-active

.PHONY: venv-clean
venv-clean:
ifndef COMPONENT
	$(error COMPONENT is required. Usage: make venv-clean COMPONENT=packages/shopping-assistant [GROUP=dev|prod])
endif
	@python3 scripts/clean_venv.py --repo-root $(REPO_ROOT) --component $(COMPONENT) $(if $(GROUP),--group $(GROUP),--clear-info)
	@echo ""
	@echo "----------------------------------------"
	@$(MAKE) -s venv-get-active

.PHONY: venv-create-all
venv-create-all:
	@echo "Creating virtual environments for all components..."
	@for component in $$(python3 scripts/list_components.py --repo-root $(REPO_ROOT)); do \
		echo ""; \
		echo "==> Creating venv for $$component (GROUP=$(if $(GROUP),$(GROUP),prod))..."; \
		$(MAKE) venv-create COMPONENT=$$component GROUP=$(if $(GROUP),$(GROUP),prod) || exit 1; \
	done
	@echo ""
	@echo "✓ All virtual environments created successfully"
	@echo ""
	@echo "----------------------------------------"
	@$(MAKE) -s venv-get-active

.PHONY: venv-clean-all
venv-clean-all:
	@echo "Cleaning virtual environments for all components..."
	@for component in $$(python3 scripts/list_components.py --repo-root $(REPO_ROOT)); do \
		echo ""; \
		echo "==> Cleaning venv for $$component$(if $(GROUP), (GROUP=$(GROUP)),)..."; \
		python3 scripts/clean_venv.py --repo-root $(REPO_ROOT) --component $$component $(if $(GROUP),--group $(GROUP),--clear-info); \
	done
	@echo ""
	@echo "✓ All virtual environments cleaned successfully"
	@echo ""
	@echo "----------------------------------------"
	@$(MAKE) -s venv-get-active

.PHONY: venv-refresh
venv-refresh:
ifndef COMPONENT
	$(error COMPONENT is required. Usage: make venv-refresh COMPONENT=packages/shopping-assistant [FIX=true])
endif
	@python3 scripts/refresh_info_json.py --repo-root $(REPO_ROOT) --component $(COMPONENT) $(if $(filter true,$(FIX)),--fix-active,)
	@echo ""
	@echo "----------------------------------------"
	@$(MAKE) -s venv-get-active

.PHONY: venv-refresh-all
venv-refresh-all:
	@echo "Refreshing .info.json for all components..."
	@failed=0; \
	for component in $$(python3 scripts/list_components.py --repo-root $(REPO_ROOT)); do \
		echo ""; \
		echo "==> Refreshing $$component..."; \
		if ! python3 scripts/refresh_info_json.py --repo-root $(REPO_ROOT) --component $$component $(if $(filter true,$(FIX)),--fix-active,); then \
			failed=$$((failed + 1)); \
		fi; \
	done; \
	echo ""; \
	if [ $$failed -eq 0 ]; then \
		echo "✓ All .info.json files refreshed successfully"; \
	else \
		echo "⚠ $$failed component(s) had validation errors"; \
		exit 1; \
	fi
	@echo ""
	@echo "----------------------------------------"
	@$(MAKE) -s venv-get-active

.PHONY: venv-get-active venv-switch-all
venv-get-active:
	@python3 scripts/get_active_venv.py --repo-root $(REPO_ROOT)

venv-switch-all:
ifndef TARGET
	$(error TARGET is required. Usage: make venv-switch-all TARGET=dev)
endif
	@echo "Switching virtual environments for all components..."
	@for component in $$(python3 scripts/list_components.py --repo-root $(REPO_ROOT)); do \
		echo ""; \
		echo "==> Switching venv for $$component (TARGET=$(TARGET))..."; \
		$(MAKE) venv-switch COMPONENT=$$component TARGET=$(TARGET) || exit 1; \
	done
	@echo ""
	@echo "✓ All virtual environments switched to $(TARGET) successfully"
	@echo ""
	@echo "----------------------------------------"
	@$(MAKE) -s venv-get-active

# ========================================
# Venv Lockfile Targets
# ========================================

.PHONY: venv-lockfile
venv-lockfile:
ifndef COMPONENT
	$(error COMPONENT is required. Usage: make venv-lockfile COMPONENT=packages/shopping-assistant [BUILD_MODE=local|linux/amd64])
endif
	@python3 scripts/build_venv_lockfile.py \
		--repo-root $(REPO_ROOT) \
		--component $(COMPONENT) \
		--build-mode $(if $(BUILD_MODE),$(BUILD_MODE),local)

.PHONY: venv-lockfile-all
venv-lockfile-all:
	@python3 scripts/build_venv_lockfile.py \
		--repo-root $(REPO_ROOT) \
		--all-components \
		--build-mode $(if $(BUILD_MODE),$(BUILD_MODE),local)


.PHONY: venv-switch
venv-switch:
ifndef COMPONENT
	$(error COMPONENT is required. Usage: make venv-switch COMPONENT=packages/shopping-assistant TARGET=dev)
endif
ifndef TARGET
	$(error TARGET is required. Usage: make venv-switch COMPONENT=packages/shopping-assistant TARGET=dev)
endif
	@python3 scripts/switch_venv.py --repo-root $(REPO_ROOT) --component $(COMPONENT) --target $(TARGET)
	@echo ""
	@echo "----------------------------------------"
	@$(MAKE) -s venv-get-active

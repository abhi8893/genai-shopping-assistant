.PHONY: all venv-switch-all venv-repair-refs venv-repair-refs-all


REPO_ROOT := $(abspath $(PWD))
PYTHON_VERSION ?= 3.12
export DOCKER_BUILDKIT=1
export REPO_ROOT

APP_COMPOSE=platform/app/docker-compose.yml
APP_COMPOSE_DEV=platform/app/docker-compose.dev.yml
LANGFUSE_COMPOSE=platform/observability/docker-compose.langfuse.yml
comma := ,
SERVICES_NORMALIZED := $(subst $(comma), ,$(SERVICES))


langfuse-dev:
	set -a; \
	. platform/observability/.env; \
	. platform/observability/.env.dev; \
	set +a; \
	docker compose \
		-p langfuse-dev \
		-f $(LANGFUSE_COMPOSE) \
		up -d

langfuse-prod:
	set -a; \
	. platform/observability/.env; \
	set +a; \
	docker compose \
		-p langfuse-prod \
		-f $(LANGFUSE_COMPOSE) \
		up -d


# Example usage: make app-dev SERVICES=shopping-assistant,ecom-backend

app-dev:
	set -a; \
	. platform/app/.env; \
	. platform/app/.env.dev; \
	set +a; \
	docker compose \
		-p app-dev \
		-f $(APP_COMPOSE) \
		-f $(APP_COMPOSE_DEV) \
		up -d $(SERVICES_NORMALIZED)

app-prod:
	set -a; \
	. platform/app/.env; \
	set +a; \
	docker compose \
		-p app-prod \
		-f $(APP_COMPOSE) \
		up -d $(SERVICES_NORMALIZED)

local-run-dev:
	make langfuse-dev
	make app-dev

local-run-prod:
	make langfuse-prod
	make app-prod

# TODO: Adhoc way to ingest products into vectorstore
ingest-products-vectordb:
	uv run --python services/shopping-assistant/.venv services/shopping-assistant/scripts/ingest_product_data_into_vectorstore.py


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


.PHONY: venv-repair-refs
venv-repair-refs:
ifndef COMPONENT
	$(error COMPONENT is required. Usage: make venv-repair-refs COMPONENT=packages/shopping-assistant [TARGET=dev])
endif
	@python3 scripts/repair_venv_references.py --venv-dir $(REPO_ROOT)/$(COMPONENT) $(if $(TARGET),--target $(TARGET),)

.PHONY: venv-repair-refs-all
venv-repair-refs-all:
	@echo "Repairing venv references for all components..."
	@for component in $$(python3 scripts/list_components.py --repo-root $(REPO_ROOT)); do \
		echo ""; \
		echo "==> Repairing venv refs for $$component..."; \
		python3 scripts/repair_venv_references.py --venv-dir $(REPO_ROOT)/$$component $(if $(TARGET),--target $(TARGET),); \
	done
	@echo ""
	@echo "✓ All venv references repaired successfully"


.PHONY: venv-pin-python
venv-pin-python:
	@cd $(REPO_ROOT)/$(if $(COMPONENT),$(COMPONENT),) && uv python pin $(PYTHON_VERSION)

.PHONY: venv-pin-python-all
venv-pin-python-all:
	@echo "Pinning Python $(PYTHON_VERSION) for root and all components..."
	@echo ""
	@echo "==> Pinning Python $(PYTHON_VERSION) for repo root..."
	@cd $(REPO_ROOT) && uv python pin $(PYTHON_VERSION)
	@for component in $$(python3 scripts/list_components.py --repo-root $(REPO_ROOT)); do \
		echo ""; \
		echo "==> Pinning Python $(PYTHON_VERSION) for $$component..."; \
		cd $(REPO_ROOT)/$$component && uv python pin $(PYTHON_VERSION) || exit 1; \
	done
	@echo ""
	@echo "✓ Python $(PYTHON_VERSION) pinned for root and all components"

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

.PHONY: venv-unswitch
venv-unswitch:
ifndef COMPONENT
	$(error COMPONENT is required. Usage: make venv-unswitch COMPONENT=packages/shopping-assistant)
endif
	@python3 scripts/unswitch_venv.py --repo-root $(REPO_ROOT) --component $(COMPONENT)
	@echo ""
	@echo "----------------------------------------"
	@$(MAKE) -s venv-get-active

.PHONY: venv-unswitch-all
venv-unswitch-all:
	@echo "Unswitching virtual environments for all components..."
	@for component in $$(python3 scripts/list_components.py --repo-root $(REPO_ROOT)); do \
		echo ""; \
		echo "==> Unswitching venv for $$component..."; \
		$(MAKE) venv-unswitch COMPONENT=$$component || exit 1; \
	done
	@echo ""
	@echo "✓ All virtual environments unswitched"
	@echo ""
	@echo "----------------------------------------"
	@$(MAKE) -s venv-get-active

.PHONY: direnv-setup
direnv-setup:
	@echo "Setting up .envrc files..."
	@python3 scripts/setup_direnv.py --repo-root $(REPO_ROOT)
	@echo ""
	@echo "✓ .envrc files created and allowed"



show-gone-branches:
	@if [ "$(DELETE)" == "TRUE" ]; then \
		echo "Deleting gone branches..."; \
		for branch in $$(git for-each-ref --format '%(refname) %(upstream:track)' refs/heads | awk -v delete=TRUE '$$2 == "[gone]" {sub("refs/heads/", "", $$1); print $$1}'); do \
			echo "Deleting branch $$branch..."; \
			git branch -D $$branch; \
		done; \
		echo ""; \
		echo "✓ Gone branches deleted"; \
	else \
		echo "Listing gone branches...\n"; \
		git for-each-ref --format '%(refname) %(upstream:track)' refs/heads | awk '$$2 == "[gone]" {sub("refs/heads/", "", $$1); print "- " $$1}'; \
		echo ""; \
		echo "Run 'make show-gone-branches DELETE=TRUE' to delete these branches"; \
	fi


test:
	. ./packages/shopping-assistant/.venv/bin/activate
	

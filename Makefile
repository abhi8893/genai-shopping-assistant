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
	if [ "$(CI)" = "true" ]; then \
		. platform/app/.env.ci; \
	else \
		. platform/app/.env; \
	fi; \
	set +a; \
	if [ "$(BUILD_ONLY)" = "true" ]; then \
		docker compose \
			-p app-prod \
			-f $(APP_COMPOSE) \
			build $(SERVICES_NORMALIZED); \
	else \
		docker compose \
			-p app-prod \
			-f $(APP_COMPOSE) \
			up -d $(SERVICES_NORMALIZED); \
	fi

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


test-package:
	make venv-create COMPONENT=packages/$(PACKAGE) GROUP=test MISSING_ONLY=true PRINT_SUMMARY=false
	cd packages/$(PACKAGE) && source .venv-test/bin/activate && pytest -m "not ci"
	

slugify:
	@echo "$(STR)" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$$//g'


.PHONY: setup-project-cli
setup-project-cli:
	@echo "Setting up root virtual environment for project CLI..."
	@uv venv --clear --python $(PYTHON_VERSION) /tmp/.venv-temp
	@uv pip install --python /tmp/.venv-temp -e packages/project
	@. /tmp/.venv-temp/bin/activate && project venv create --overwrite root --group dev
	@echo "✓ Project CLI installed in root .venv"
	@rm -rf /tmp/.venv-temp
	@. .venv-dev/bin/activate && project venv switch root --target dev

	@echo ""
	@echo "Run 'source .venv/bin/activate' to use 'project' commands natively"
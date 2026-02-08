# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**GenAI Shopping Assistant** is a multi-agent LLM system that serves as an intelligent shopping companion for e-commerce websites. The project focuses primarily on the GenAI Shopping Assistant as the core component, with auxiliary services demonstrating real-world integration.

### Core Component: GenAI Shopping Assistant
- **Multi-Agent System**: RouterAgent, ProductSearchAgent, ShopperAgent, CustomerServiceAgent
- **Natural Language Interface**: Users shop conversationally through specialized agents
- **Intelligent Orchestration**: Central RouterAgent directs queries to appropriate specialized agents

### Auxiliary Services (Supporting Infrastructure)
The system includes essential services that demonstrate how the GenAI Shopping Assistant integrates in a real environment:
- **ecom-backend**: E-commerce operations (carts, products, users)
- **product-retriever**: Vector-based semantic search
- **memory**: Session and context management

### Architecture Evolution

**Current State (v0.x)**:
- Main component: shopping-assistant (GenAI chatbot)
- Tightly coupled auxiliary services for demo purposes (ecom-backend, product-retriever, memory)
- All services work together as an integrated system

**Target State (v1.x+)**:
- Main component: shopping-assistant (standalone GenAI chatbot)
- **Semi-coupled services** (Build-YOS - Build Your Own Service): memory service with swappable API design
- **Lightly coupled services** (Bring-YOS - Bring Your Own Service): ecom-backend, product-retriever with standard platform integrations (e.g., Shopify)

## Monorepo Structure

This is a Python monorepo organized around the **GenAI Shopping Assistant** as the primary focus:

- **`packages/`** - Core reusable packages
  - `shopping-assistant/` - **Primary Package**: Multi-agent LLM system with agent definitions, graph orchestration, and GenAI capabilities
- **`services/`** - Deployable microservices demonstrating integration
  - `shopping-assistant/` - **Core Service**: Gradio web app showcasing the GenAI Shopping Assistant
  - `ecom-backend/` - **Auxiliary Service**: FastAPI backend for e-commerce operations (demonstrates integration)
  - `product-retriever/` - **Auxiliary Service**: Vector-based product search (demonstrates integration)
- **`platform/`** - Infrastructure and deployment configuration
  - `app/` - Docker Compose files for running the full application stack (Weaviate, Ollama, services)
  - `observability/` - Langfuse deployment for LLM observability
- **`data/`** - Product data and datasets
- **`notebooks/`** - Jupyter notebooks for experimentation

## Common Commands

### Code Quality

```bash
# Run all pre-commit hooks on all files
make check-all

# Run all hooks on a specific file
make check-all FILE=path/to/file.py

# Run linting only (ruff)
make check-lint

# Run formatting only (ruff-format)
make check-format

# Run secret scanning only (gitleaks)
make check-secrets

# Run a specific pre-commit hook
make check-hook-<hook-name>
```

The repo uses `ruff` for linting and formatting (configured in `ruff.toml`). Pre-commit hooks are defined in `.pre-commit-config.yaml` and include:
- Ruff linting with auto-fix
- Ruff formatting
- Secret scanning with gitleaks (configured in `.gitleaks.toml`)
- YAML validation
- GitHub Actions workflow validation (actionlint)
- Trailing whitespace removal
- End-of-file fixers
- Merge conflict detection
- No-commit-to-branch (blocks commits to `main` and `develop`)

### Running the Application Locally

```bash
# Run everything in development mode (Langfuse + App stack)
make local-run-dev

# Run everything in production mode
make local-run-prod

# Run only Langfuse (observability platform)
make langfuse-dev  # or make langfuse-prod

# Run only the app stack (Weaviate, Ollama, shopping-assistant, ecom-backend)
make app-dev  # or make app-prod
```

The application stack includes:
- **Weaviate** - Vector database for semantic product search
- **Ollama** - Local LLM inference (used by Weaviate modules)
- **shopping-assistant** - Main chatbot service (Gradio UI)
- **ecom-backend** - E-commerce API (SQLite database)

### Running Individual Services

**Ecom Backend:**
```bash
cd services/ecom-backend
python app.py  # Runs on http://localhost:8000
# Swagger UI: http://localhost:8000/api/v1/docs
```

**Shopping Assistant Service:**
```bash
cd services/shopping-assistant
python app.py  # Runs Gradio app
```

### Data Ingestion

```bash
# Ingest product data into vector database (adhoc script)
make ingest-products-vectordb
```

## Virtual Environment Management

Refer to `.claude/rules/venv-management.md` for detailed virtual environment management guidelines.

## GenAI Shopping Assistant: Multi-Agent Architecture

The core **shopping-assistant** uses a multi-agent architecture defined in `packages/shopping-assistant/src/shopping_assistant/`:

1. **RouterAgent** (`agent_definitions/router.py`) - **Central Orchestrator**: Classifies user intent and intelligently routes to specialized agents
2. **ProductSearchAgent** (`agent_definitions/product_search.py`) - **Product Discovery Expert**: Handles product discovery via semantic search and natural language understanding
   - Parses complex queries to extract category, subcategory, price range, attributes
   - Generates clarifying responses when user intent is ambiguous
   - Retrieves products from Weaviate vector store with semantic understanding
3. **ShopperAgent** (`agent_definitions/shopping_actions.py`) - **Shopping Actions Specialist**: Performs cart operations, checkout, order management, and purchase workflows
4. **CustomerServiceAgent** (`agent_definitions/customer_service.py`) - **Support Specialist**: Handles general inquiries, customer service, and non-shopping conversations

### Agent Configuration & Orchestration
- **Configuration**: Agent prompts, LLM models, routing rules in `services/shopping-assistant/config.yml`
- **Orchestration**: LangGraph-based coordination in `packages/shopping-assistant/src/shopping_assistant/graph/`
- **Multi-Agent Flow**: RouterAgent → Specialized Agent → Response Generation → User

This multi-agent system enables the GenAI Shopping Assistant to handle diverse shopping scenarios with specialized expertise while maintaining a unified conversational experience.

## Auxiliary Service: Ecom Backend Architecture

The `services/ecom-backend/` is an **auxiliary service** that demonstrates how the GenAI Shopping Assistant integrates with e-commerce systems. It follows a 3-tier architecture:

- **API Layer** (`api/v1/`) - FastAPI routers, request/response schemas
- **Service Layer** (`domains/*/service.py`) - Business logic
- **Repository Layer** (`domains/*/repository.py`) - Database access via SQLAlchemy ORM

Domains are organized by entity:
- `domains/products/` - Product catalog APIs
- `domains/carts/` - Shopping cart APIs  
- `domains/users/` - User management APIs

Database migrations are managed with Alembic (`migrations/`).

**Note**: In the target architecture (v1.x+), this service will be replaceable with standard e-commerce platforms (Shopify, WooCommerce) via Bring-YOS integrations.

## Environment Configuration

Environment variables are split across multiple locations:

- **Root `.env`** - Shared configuration
- **`platform/app/.env`** and **`platform/app/.env.dev`** - App stack configuration (ports, API keys)
- **`platform/observability/.env`** and **`platform/observability/.env.dev`** - Langfuse configuration

The Makefile uses `REPO_ROOT` to reference paths across the monorepo when building Docker images.

## Development Workflow

1. This repo uses `uv` for Python package management (see CI workflow in `.github/workflows/main.yml`)
2. Pre-commit hooks run automatically on `git commit`
3. CI runs code quality checks on all branches (linting, formatting, YAML validation)
4. The `no-commit-to-branch` hook blocks direct commits to `main` and `develop` branches
5. Python 3.12 is the target version

## Key Integration Points

The **GenAI Shopping Assistant** integrates with auxiliary services to demonstrate a complete shopping experience:

- **GenAI Shopping Assistant → Ecom Backend**: The multi-agent system calls the ecom backend API at `ECOM_API_BASE_URL` for cart/product operations
- **GenAI Shopping Assistant → Weaviate**: Product embeddings are stored in Weaviate for semantic search by the ProductSearchAgent
- **All Services → Langfuse**: LLM tracing and observability for monitoring multi-agent performance (configured via `LANGFUSE_*` env vars)
- **Weaviate → Ollama**: Weaviate uses Ollama for text embeddings (`text2vec-ollama` module)

**Future Integration Architecture**:
- **Build-YOS APIs**: Standardized interfaces for memory and context services
- **Bring-YOS Connectors**: Adapters for standard e-commerce platforms (Shopify, WooCommerce)
- **Service Discovery**: Dynamic service registration and configuration for swappable components

## Testing

Currently, tests are excluded from ruff checks (see `ruff.toml`). Test files follow the pattern `test_*.py` and use pytest.

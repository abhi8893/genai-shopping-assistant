# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]

## [v0.1.0.rc.0] - 2026-03-07

### 1st Release

A complete multi-agent LLM system for intelligent shopping assistance. This first release includes the core `shopping-assistant` package and service with four specialized agents orchestrated by LangGraph, an auxiliary `ecom-backend` service for e-commerce operations, and integration with Weaviate for semantic search and Langfuse for observability. The entire stack is designed to run locally via Docker Compose for a seamless development and deployment experience.

**Main Component**: `shopping-assistant` service (FastAPI) exposing the multi-agent system via REST API

**Auxiliary Services**: `ecom-backend` (e-commerce API for products, carts, users)

**Out-of-the-box Services**: Weaviate (vector database), Ollama (local embeddings), Langfuse (observability)

### `packages/shopping-assistant` ([v0.1.0.rc.0] - 2026-03-07)

The core Python package implementing the multi-agent LLM system. Includes four specialized agents (RouterAgent for intent classification, ProductSearchAgent for semantic search via Weaviate, ShoppingActionsAgent for cart operations via EcomAPIClient, and CustomerServiceAgent for support), LangGraph-based orchestration, optional Langfuse observability, and dual interfaces (CLI and Gradio web UI).

See `packages/shopping-assistant/CHANGELOG.md` for details.


### `services/shopping-assistant` ([v0.1.0.rc.0] - 2026-03-07)

FastAPI web service wrapping the `shopping-assistant` package and exposing it via REST API. Provides core endpoints: `/health` for health checks, `/` for service info, and `POST /chat` for conversational interactions. Supports thread-based multi-turn conversations with user tracking. Note: Streaming chat is not supported in this release.

See `services/shopping-assistant/CHANGELOG.md` for details.


### `services/ecom-backend` ([v0.1.0.rc.0] - 2026-03-07)

Auxiliary FastAPI service providing e-commerce operations required for the GenAI Shopping Assistant. Implements a 3-tier architecture (API, Service, Repository layers) across three domains: Products (with category/subcategory hierarchy and keyword search), Carts (with CRUD operations and amount calculations), and Users. Uses SQLite for persistence with Alembic for schema management.

See `services/ecom-backend/CHANGELOG.md` for details.
# shopping-assistant

The core GenAI Shopping Assistant package. A multi-agent LLM system that provides a conversational shopping experience through specialized agents orchestrated by LangGraph.

---

## Setting Up Dev Environment

### Prerequisites

- Python 3.12
- [`uv`](https://docs.astral.sh/uv/) — used for virtual environment and dependency management

### Option A: Using Make targets (recommended)

From the **repo root**:

```bash
# Create the dev virtual environment (editable install)
make venv-create COMPONENT=packages/shopping-assistant GROUP=dev

# Activate it
source packages/shopping-assistant/.venv-dev/bin/activate
```

To switch between `dev` and `prod` environments:

```bash
# Switch active venv to dev
make venv-switch COMPONENT=packages/shopping-assistant TARGET=dev

# Then activate
source packages/shopping-assistant/.venv/bin/activate
```

> See the repo root `README.md` and `.claude/rules/venv-management.md` for full venv management documentation.

### Option B: Manual uv install (editable)

From the **repo root**:

```bash
cd packages/shopping-assistant

# Create a virtual environment
uv venv --python 3.12 .venv-dev

# Activate it
source .venv-dev/bin/activate

# Install the package in editable mode with dev dependencies
uv pip install -e "." --group dev
```

## Setting Up External Connections

The package connects to three external services: **Weaviate** (vector search), **Ecom Backend API** (cart and product operations), and an **LLM provider** (OpenAI, Anthropic, or Cohere).

### Get a starter `.env` file

Run the following to scaffold a new project directory with an example config and `.env.example`:

```bash
shopping-assistant create new .
```

This creates `.env.example` (and `config/config.yml`) in the current directory. Copy it to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Weaviate

The package uses `WeaviateConnectionManager` (from `shopping_assistant.product_retrieval`) to manage the Weaviate connection lifecycle. It is constructed from the following env vars:

| Variable | Description | Default |
|---|---|---|
| `WEAVIATE_HTTP_HOST` | Weaviate HTTP host | `localhost` |
| `WEAVIATE_HTTP_PORT` | Weaviate HTTP port | `8080` |
| `WEAVIATE_HTTP_SECURE` | Use HTTPS | `false` |
| `WEAVIATE_GRPC_HOST` | Weaviate gRPC host | `localhost` |
| `WEAVIATE_GRPC_PORT` | Weaviate gRPC port | `50051` |
| `WEAVIATE_GRPC_SECURE` | Use gRPC TLS | `false` |

> For Weaviate setup (Docker, product ingestion, etc.) see the repo root `README.md`.

### Ecom Backend API

The package uses `EcomAPIClient` (from `shopping_assistant.external.ecom_api_client.client`) for all cart and product operations. It is initialised with a `base_url` and optional `Credentials(user_id=...)`.

| Variable | Description | Example |
|---|---|---|
| `ECOM_API_BASE_URL` | Base URL of the ecom backend | `http://localhost:8000/api/v1` |

### LLM Provider API Keys

The package supports OpenAI, Anthropic, and Cohere as LLM providers. Set the key for whichever provider your `config.yml` is configured to use:

| Variable | Provider |
|---|---|
| `OPENAI_API_KEY` | OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic |
| `CO_API_KEY` | Cohere |

Optional base URL overrides (useful for proxies or Azure):

| Variable | Description |
|---|---|
| `OPENAI_BASE_URL` | Custom OpenAI-compatible endpoint |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint |
| `ANTHROPIC_BASE_URL` | Custom Anthropic endpoint |
| `CO_API_URL` | Custom Cohere endpoint |

### Observability (Langfuse)

LLM traces are sent to [Langfuse](https://langfuse.com). These are optional but recommended for monitoring agent behaviour:

| Variable | Description | Default |
|---|---|---|
| `LANGFUSE_PUBLIC_KEY` | Langfuse project public key | — |
| `LANGFUSE_SECRET_KEY` | Langfuse project secret key | — |
| `LANGFUSE_BASE_URL` | Langfuse server URL | `http://localhost:3000` |

> For self-hosted Langfuse setup see `platform/observability/`.
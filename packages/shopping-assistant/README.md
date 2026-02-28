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

---

## Installing the Package

> **Note:** `shopping-assistant` is not currently published to PyPI. Install directly from GitHub.

### Latest released version

```bash
uv pip install "git+https://github.com/abhi8893/genai-shopping-assistant.git@<version>#subdirectory=packages/shopping-assistant"
```

Replace `<version>` with a release tag (e.g. `v0.1.0`). Available releases can be found on the [GitHub releases page](https://github.com/abhi8893/genai-shopping-assistant/releases).

### Current develop version

To install the latest unreleased code from the `main` branch:

```bash
uv pip install "git+https://github.com/abhi8893/genai-shopping-assistant.git@develop#subdirectory=packages/shopping-assistant"
```

---

## Package Structure

```bash
src/shopping_assistant/
├── agent_definitions/          # Agent prompt definitions and configurations
│   ├── router.py               # RouterAgent — classifies intent and routes to specialist agents
│   ├── product_search.py       # ProductSearchAgent — semantic product discovery via Weaviate
│   ├── shopping_actions.py     # ShoppingActionsAgent — cart, checkout, and order operations
│   └── customer_service.py     # CustomerServiceAgent — general support and FAQs
├── graph/                      # LangGraph orchestration
│   ├── graph.py                # Multi-agent graph definition and entrypoint
│   ├── types.py                # Graph state types
│   └── utils.py                # Graph utility helpers
├── external/
│   └── ecom_api_client/        # HTTP client for the Ecom Backend API
│       ├── client.py           # EcomAPIClient — top-level client
│       ├── credentials.py      # Credentials model
│       ├── http.py             # Base HTTP transport
│       └── resources/
│           ├── carts/          # Cart API resource (client + types)
│           └── products/       # Products API resource (client + types)
├── tools/                      # Agent tools
│   └── cart_actions.py         # ShoppingActions agent cart action tools wrapping EcomAPIClient cart operations
├── observability/
│   ├── utils.py                # Langfuse + logfire setup
│   └── preflight.py            # Connectivity pre-flight checks
├── config/
│   └── config.yml              # Default agent and LLM configuration
├── chat.py                     # Chat — high-level Python API (CLI and web UI)
├── cli.py                      # CLI entrypoint (shopping-assistant commands)
├── config.py                   # Config loader
├── product_retrieval.py        # product retrieval with weaviate
├── env.py                      # .env file loader
└── types.py                    # Shared types
```

---

## Architecture

The package implements a **multi-agent LangGraph pipeline**. A central `RouterAgent` classifies every user message and dispatches it to one of three specialist agents. Each agent runs independently and writes its response back to the shared graph `State`.

### Agents

| Agent | Role | LLM Framework | External Dependency |
|---|---|---|---|
| `RouterAgent` | Classifies user intent and routes to the correct specialist | OpenAI structured output (`parse`) | — |
| `ProductSearchAgent` | Parses product query, runs semantic search, returns matching products | OpenAI chat | Weaviate (vector DB) |
| `ShoppingActionsAgent` | Manages cart operations (add, remove, view, checkout) via function tools | OpenAI Agents SDK (`Agent` + `Runner`) | Ecom Backend API |
| `CustomerServiceAgent` | Handles general support, FAQs, and off-topic queries | OpenAI chat | — |

### Graph Flow

```mermaid
graph TD
    User(["User message"])
    START(["START"])
    END(["END"])
    Response(["Agent response"])

    User --> START
    START -->|"conditional edge"| Router

    subgraph Router["RouterAgent"]
        R["Classify intent → <br> product_search | shopping_actions | customer_service"]
    end

    Router -->|product_search| PS
    Router -->|shopping_actions| SA
    Router -->|customer_service| CS

    subgraph PS["ProductSearchAgent"]
        PS1["Parse query details <br> (category, price range)"]
        PS2["Semantic search <br> via Weaviate"]
        PS1 --> PS2
    end

    subgraph SA["ShoppingActionsAgent"]
        SA1["OpenAI Agents SDK<br>with function tools"]
        SA2["Cart operations<br>via EcomAPIClient"]
        SA1 --> SA2
    end

    subgraph CS["CustomerServiceAgent"]
        CS1["General support<br>& FAQ response"]
    end

    PS --> END
    SA --> END
    CS --> END
    END --> Response

    PS2 <-->|"WeaviateConnectionManager"| Weaviate[("Weaviate<br>vector DB")]
    SA2 <-->|"EcomAPIClient"| EcomAPI[("Ecom<br>Backend API")]
```

### Graph State

All agents read from and write to a shared `State` object:

| Field | Type | Description |
|---|---|---|
| `messages` | `list` | Accumulated OpenAI-format conversation messages |
| `prev_recommended_products` | `list[ProductVectorDBRecord] \| None` | Products recommended in the current session |
| `last_response_agent` | `str \| None` | Name of the agent that produced the last response |


---

## RouterAgent

The `RouterAgent` is the graph entrypoint. It inspects the conversation history and returns the name of the downstream route to execute. It never produces a user-facing message itself. It is based on OpenAI's `parse` structured output.

The three routes and representative examples from the default config:

| Route | Example queries |
|---|---|
| `product_search` | "I am looking for headphones under 2000 rupees.", "Do you have wind cheaters in red?" |
| `shopping_actions` | "Can you add this to the cart?", "I want to place an order for this product." |
| `customer_service` | "Hello!", "Can you tell me the return policy?" |

### Prompt

Configured under `agents.router` in `config.yml`. The system prompt instructs the agent to analyse the conversation and select the correct route. The `{downstream_routes_desc}` placeholder is populated at runtime from the `downstream_routes` list, which includes each route's name, description, and example queries.

```
You are a helpful ecom shopping assistant tasked with redirecting the user
to the appropriate specialized downstream routes.
Analyze the provided conversation history with the user to re-examine if
you are the right agent to answer the user's query.
...
{downstream_routes_desc}

Please respond ONLY with the name of the appropriate downstream route
based on the user's query.
```

### Python API

```python
from shopping_assistant.agent_definitions import RouterAgent
from shopping_assistant.config import load_config

config = load_config()  # loads default config.yml
router = RouterAgent(config=config["agents"]["router"])
```

`RouterAgent` constructor accepts:

| Parameter | Type | Description |
|---|---|---|
| `config` | `dict` | Agent config block (`config["agents"]["router"]`) |
| `openai_client` | `openai.OpenAI \| None` | Optional pre-configured OpenAI client; defaults to `openai.OpenAI()` |

### Usage

`RouterAgent.run(state)` is called by LangGraph as a conditional edge from `START`. It can also be called directly:

```python
from shopping_assistant.agent_definitions import RouterAgent
from shopping_assistant.config import load_config
from shopping_assistant.graph.types import State

config = load_config()
router = RouterAgent(config=config["agents"]["router"])

queries = [
    "I am looking for headphones under 2000 rupees",
    "Add the first item to my cart",
    "What is your return policy?",
]

for query in queries:
    state = State(messages=[{"role": "user", "content": query}])
    route = router.run(state)
    print(f"Query : {query!r}")
    print(f"Route : {route!r}")
    print()
```

### Output

Returns one of the three route name strings — used by LangGraph to select the next node:

```
"product_search" | "shopping_actions" | "customer_service"
```

Example output:

```
Query : 'I am looking for black sunglasses under 100$'
Route : 'product_search'

Query : 'Add the first item to my cart'
Route : 'shopping_actions'

Query : 'What is your return policy?'
Route : 'customer_service'
```

---

## CustomerServiceAgent

Handles general chitchat and customer service queries — anything not related to product discovery or cart operations. It uses a plain OpenAI chat completion (no structured output, no tools).

### Prompt

Configured under `agents.customer_service` in `config.yml`. The agent is instructed to handle general support and chitchat, and to use the conversation history to understand which agent has previously responded.

```
You are a helpful customer service agent for an e-commerce website.
Answer any general chitchat questions as well as specific customer service
questions for the user.

Analyze the provided conversation history with the user to re-examine if
you are the right agent to answer the user's query.
...
DO NOT include your designated name or alias in your response.
```

### Python API

```python
from shopping_assistant.agent_definitions import CustomerServiceAgent
from shopping_assistant.config import load_config

config = load_config()
agent = CustomerServiceAgent(config=config["agents"]["customer_service"])
```

`CustomerServiceAgent` constructor accepts:

| Parameter | Type | Description |
|---|---|---|
| `config` | `dict` | Agent config block (`config["agents"]["customer_service"]`) |
| `openai_client` | `openai.OpenAI \| None` | Optional pre-configured OpenAI client; defaults to `openai.OpenAI()` |

### Usage

```python
from shopping_assistant.graph.types import State

queries = [
    "Hello! How are you?",
    "What is your return policy?",
    "I have a complaint about a product I received.",
]

for query in queries:
    state = State(messages=[{"role": "user", "content": query}])
    new_state = agent.run(state)
    print(f"User  : {query!r}")
    print(f"Agent : {new_state.messages[-1]['content']!r}")
    print()
```

### Output

`run(state)` returns an updated `State` with the agent's reply appended to `messages`. The response is prefixed with `"Customer Service Agent: "`.

```
User  : 'Hello! How are you?'
Customer Service Agent: Hello! I'm doing well, thank you for asking. How can I assist you today?

User  : 'What is your return policy?'
Customer Service Agent: Our return policy allows you to return most items within
30 days of receipt for a full refund. Items must be in their original condition, unused,
and with all tags and packaging intact. Some exceptions may apply, such as for personalized
or final sale items.

If you have a specific item in mind or need help with the return process, feel free to ask!'

User  : 'I have a complaint about a product I received.'
Customer Service Agent: I'm here to help you with your complaint. Could you please
provide more details about the product and the issue you're experiencing? This information
will help me assist you better.
```

---

## ProductSearchAgent

Handles product discovery. It first uses OpenAI structured output to parse the user query into category, subcategory, and price range. If the category cannot be inferred, it returns a clarification response. Otherwise, it runs a semantic `near_text` search against the Weaviate `products` collection and returns the matching results.

### Prompt

Configured under `agents.product_search` in `config.yml`. The system prompt includes the catalog hierarchy tree and the previously recommended products, and instructs the agent to follow a structured parsing step:

```
You are a shopping assistant, who helps users find products in an e-commerce store.
You are given the product catalog hierarchy as follows:

{catalog_hierarchy_tree}

You previously recommended the following products to the user:

{prev_recommended_products}

STEPS:
1. Identify the category from the user query => `category`
   IMPORTANT: ONLY IF NO category can be inferred, return None and proceed to step 2A,
   else jump to step 2B
2A. Draft a clarification response as `product_clarification_response`. NOW EXIT.
2B. Identify the subcategory => `subcategory`
3. Identify the price range (min_price, max_price) => `price_range`
4. Rephrase the user query to a specific retrieval query => `retrieval_query`
```

The default catalog hierarchy (from `config.yml`):

```
accessories:  bag, sunglasses
apparel:      dress, skirt, top blouse sweater
footwear:     shoes
jewelry:      bracelet, earrings, necklace
```

### Connection with Weaviate

`ProductSearchAgent` accepts a `WeaviateClient` at construction time. The client is passed through to `retrieve_products()` which uses `WeaviateConnectionManager` to manage the connection lifecycle and run a `near_text` semantic search against the `products` collection.

```python
import os
import weaviate
from shopping_assistant.product_retrieval import WeaviateConnectionManager

weaviate_client = weaviate.WeaviateClient(
    connection_params=weaviate.connect.ConnectionParams(
        http={"host": os.getenv("WEAVIATE_HTTP_HOST"), "port": os.getenv("WEAVIATE_HTTP_PORT"), "secure": False},
        grpc={"host": os.getenv("WEAVIATE_GRPC_HOST"), "port": os.getenv("WEAVIATE_GRPC_PORT"), "secure": False},
    )
)
```

> Weaviate must be running and the `products` collection must be ingested. See the repo root `README.md` for setup instructions.

### Python API

```python
import os
import weaviate
from dotenv import load_dotenv
from shopping_assistant.agent_definitions import ProductSearchAgent
from shopping_assistant.config import load_config

load_dotenv(".env")
config = load_config()

weaviate_client = weaviate.WeaviateClient(
    connection_params=weaviate.connect.ConnectionParams(
        http={"host": os.getenv("WEAVIATE_HTTP_HOST"), "port": os.getenv("WEAVIATE_HTTP_PORT"), "secure": False},
        grpc={"host": os.getenv("WEAVIATE_GRPC_HOST"), "port": os.getenv("WEAVIATE_GRPC_PORT"), "secure": False},
    )
)

agent = ProductSearchAgent(
    config=config["agents"]["product_search"],
    weaviate_client=weaviate_client,
)
```

`ProductSearchAgent` constructor accepts:

| Parameter | Type | Description |
|---|---|---|
| `config` | `dict` | Agent config block (`config["agents"]["product_search"]`) |
| `openai_client` | `openai.OpenAI \| None` | Optional pre-configured OpenAI client; defaults to `openai.OpenAI()` |
| `weaviate_client` | `WeaviateClient \| None` | Weaviate client for product retrieval; defaults to `weaviate.connect_to_local()` |
| `langfuse_client` | `Langfuse \| None` | Optional Langfuse client for tracing |

### Usage

```python
from shopping_assistant.graph.types import State

queries = [
    "I am looking for black sunglasses under 100$.",
    "Do you have earrings in white colour?",
    "I am looking for gaming laptops which can run raytracing at ultra settings",
]

for query in queries:
    state = State(messages=[{"role": "user", "content": query}])
    new_state = agent.run(state)
    print(f"User  : {query!r}")
    print(new_state.messages[-1]["content"])
    print()
```

---

## ShoppingActionsAgent

Handles all cart and order operations. It uses the OpenAI Agents SDK (`Agent` + `Runner`) with function tools that wrap `EcomAPIClient`. The agent parses the user's intent, selects the appropriate tool, executes it against the Ecom Backend API, and returns a confirmation with the updated cart state.

### Prompt

Configured under `agents.shopping_actions` in `config.yml`. The system prompt is built dynamically at construction time from the available action types and their tools:

```
You are a helpful shopping assistant that can help users with their shopping needs.
Based on the user's query, you do the following:

Step 1. Parse the user's query to understand the user's intended action type
        out of the following list: {action_list}
Step 2. If no action type is identified, respond with what you can help with.
Step 3. Based on the action type, call the appropriate action tool:
        {action_detailed}
Step 4. After the action is completed, inform the user of the result.
```

The current action type is `cart`, with these tools:

| Tool | Description |
|---|---|
| `add_to_cart` | Add a product (by slug) to the cart |
| `remove_from_cart` | Remove a quantity of a product from the cart |
| `view_cart` | View all cart items and total |
| `empty_cart` | Empty the entire cart |
| `empty_item_from_cart` | Remove all quantity of a specific item |
| `get_cart_total` | Get the cart total value |

### Connection with Ecom Backend API

`ShoppingActionsAgent` does not take `EcomAPIClient` directly — it takes a `Cart` object (from `shopping_assistant.tools.cart_actions`) which wraps the client. `Cart` is initialised with an `EcomAPIClient` that holds the base URL and user credentials.

`tools.cart_actions.Cart` -> `EcomAPIClient` -> `CartsAPIClient` -> `api/v1/carts/*`

```python
import os
from dotenv import load_dotenv
from shopping_assistant.external.ecom_api_client.client import EcomAPIClient
from shopping_assistant.external.ecom_api_client.credentials import Credentials
from shopping_assistant.tools.cart_actions import Cart

load_dotenv(".env")

ecom_api_client = EcomAPIClient(
    base_url=os.getenv("ECOM_API_BASE_URL"),
    credentials=Credentials(user_id=1),
)
cart = Cart(api_client=ecom_api_client)
```

> The Ecom Backend must be running. See the repo root `README.md` for setup instructions.

### Python API

```python
from shopping_assistant.agent_definitions import ShoppingActionsAgent
from shopping_assistant.config import load_config

config = load_config()
agent = ShoppingActionsAgent(config=config["agents"]["shopping_actions"], cart=cart)
```

`ShoppingActionsAgent` constructor accepts:

| Parameter | Type | Description |
|---|---|---|
| `config` | `dict` | Agent config block (`config["agents"]["shopping_actions"]`) |
| `cart` | `Cart` | Cart instance wrapping `EcomAPIClient` |

### Usage

`run(state)` is async and must be awaited:

```python
import asyncio
from shopping_assistant.graph.types import State

queries = [
    "Add trendy-tapered-sunglasses to my cart",
    "Can I please see my cart?",
    "Update the quantity of southwest-bracelet to 2",
]

async def main():
    for query in queries:
        state = State(messages=[{"role": "user", "content": query}])
        new_state = await agent.run(state)
        print(f"User  : {query!r}")
        print(new_state.messages[-1]["content"])
        print()

asyncio.run(main())
```

### Output

`ShoppingActionsAgent.run(state)` returns an updated `State` with the agent's reply appended to `messages`, prefixed with `"Shopping Actions Agent: "`. Cart state is included inline in the response.

```
User  : 'Add trendy-tapered-sunglasses to my cart'
Shopping Actions Agent: I have added the Trendy Tapered Sunglasses to your cart. Here's what your cart currently looks like:

| Sno | Product | Slug | Qty | Amount |
|---|---|---|---|---|
| 1 | Southwest Bracelet | southwest-bracelet | 1 | $169.99 |
| 2 | Floral Choker Necklace | floral-choker-necklace | 2 | $259.98 |
| 3 | Ivy Leaf Embroidered Skirt | ivy-leaf-embroidered-skirt | 1 | $189.99 |
| 4 | Trendy Tapered Sunglasses | trendy-tapered-sunglasses | 1 | $49.99 |

**Total: $669.95**

User  : 'Can I please see my cart?'
Shopping Actions Agent: Here's what you have in your cart:

1. Southwest Bracelet: $169.99 (Quantity: 1)
2. Floral Choker Necklace: $259.98 (Quantity: 2)
3. Ivy Leaf Embroidered Skirt: $189.99 (Quantity: 1)
4. Trendy Tapered Sunglasses: $49.99 (Quantity: 1)

Your current total amount is $669.95.

User  : 'Update the quantity of southwest-bracelet to 2'
Shopping Actions Agent: The quantity of the "Southwest Bracelet" has been successfully updated to 2. Here is the current state of your cart:

| Sno | Product | Slug | Qty | Amount |
|---|---|---|---|---|
| 1 | Southwest Bracelet | southwest-bracelet | 3 | $509.97 |
| 2 | Floral Choker Necklace | floral-choker-necklace | 2 | $259.98 |
| 3 | Ivy Leaf Embroidered Skirt | ivy-leaf-embroidered-skirt | 1 | $189.99 |
| 4 | Trendy Tapered Sunglasses | trendy-tapered-sunglasses | 1 | $49.99 |

The total amount of your cart is $1009.93.
```

---

## Example Usage

The `Chat` class (`shopping_assistant.chat`) is the high-level interface that wires together all agents, the LangGraph graph, Weaviate, and the Ecom API into a single session object.

### Setup

```python
import os
import weaviate
from dotenv import load_dotenv
from shopping_assistant.chat import Chat
from shopping_assistant.config import load_config
from shopping_assistant.external.ecom_api_client.client import EcomAPIClient
from shopping_assistant.external.ecom_api_client.credentials import Credentials

load_dotenv(".env")
config = load_config()

weaviate_client = weaviate.WeaviateClient(
    connection_params=weaviate.connect.ConnectionParams(
        http={"host": os.getenv("WEAVIATE_HTTP_HOST"), "port": os.getenv("WEAVIATE_HTTP_PORT"), "secure": False},
        grpc={"host": os.getenv("WEAVIATE_GRPC_HOST"), "port": os.getenv("WEAVIATE_GRPC_PORT"), "secure": False},
    )
)

ecom_api_client = EcomAPIClient(
    base_url=os.getenv("ECOM_API_BASE_URL"),
    credentials=Credentials(user_id=1),
)

chat = Chat(
    config=config,
    weaviate_client=weaviate_client,
    ecom_api_client=ecom_api_client,
)
```

### `Chat.query` — single-turn programmatic query

Send a single message and get the agent's response as a string. Useful for programmatic usage or testing.

```python
import asyncio

response = asyncio.run(chat.query("Do you have sunglasses under $50?"))
print(response)
```

### `Chat.cli_chat` — interactive CLI session

Starts an interactive terminal chat loop. Type `\quit` to exit.

```python
import asyncio

asyncio.run(chat.cli_chat())
```

Or from the command line directly:

```bash
shopping-assistant chat --user-id 1 --env-file .env
```

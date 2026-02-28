"""Explore ProductSearchAgent: instantiate and run against sample queries."""

import os

import weaviate
from dotenv import load_dotenv
from shopping_assistant.agent_definitions import ProductSearchAgent
from shopping_assistant.config import load_config
from shopping_assistant.graph.types import State

load_dotenv("../.env")
config = load_config()

weaviate_client = weaviate.WeaviateClient(
    connection_params=weaviate.connect.ConnectionParams(
        http={
            "host": os.getenv("WEAVIATE_HTTP_HOST"),
            "port": os.getenv("WEAVIATE_HTTP_PORT"),
            "secure": os.getenv("WEAVIATE_HTTP_SECURE"),
        },
        grpc={
            "host": os.getenv("WEAVIATE_GRPC_HOST"),
            "port": os.getenv("WEAVIATE_GRPC_PORT"),
            "secure": os.getenv("WEAVIATE_GRPC_SECURE"),
        },
    )
)

agent = ProductSearchAgent(
    config=config["agents"]["product_search"],
    weaviate_client=weaviate_client,
)

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

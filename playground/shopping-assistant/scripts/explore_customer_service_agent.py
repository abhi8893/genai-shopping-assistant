"""Explore CustomerServiceAgent: instantiate and run against sample queries."""

from dotenv import load_dotenv
from shopping_assistant.agent_definitions import CustomerServiceAgent
from shopping_assistant.config import load_config
from shopping_assistant.graph.types import State

load_dotenv("../.env")

config = load_config()
agent = CustomerServiceAgent(config=config["agents"]["customer_service"])

queries = [
    "Hello! How are you?",
    "What is your return policy?",
    "I have a complaint about a product I received.",
]

for query in queries:
    state = State(messages=[{"role": "user", "content": query}])
    new_state = agent.run(state)
    print(f"User  : {query!r}")
    print(new_state.messages[-1]["content"])
    print()

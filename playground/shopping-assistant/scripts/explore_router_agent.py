"""Explore RouterAgent: instantiate and run against sample queries."""

from dotenv import load_dotenv
from shopping_assistant.agent_definitions import RouterAgent
from shopping_assistant.config import load_config
from shopping_assistant.graph.types import State

load_dotenv("../.env")
config = load_config()
router = RouterAgent(config=config["agents"]["router"])

queries = [
    "I am looking for black sunglasses under 100$",
    "Add the first item to my cart",
    "What is your return policy?",
]

for query in queries:
    state = State(messages=[{"role": "user", "content": query}])
    route = router.run(state)
    print(f"Query : {query!r}")
    print(f"Route : {route!r}")
    print()

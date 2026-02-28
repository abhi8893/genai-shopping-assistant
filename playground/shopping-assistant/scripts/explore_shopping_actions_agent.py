"""Explore ShoppingActionsAgent: instantiate and run against sample queries."""

import asyncio
import os

from dotenv import load_dotenv
from shopping_assistant.agent_definitions import ShoppingActionsAgent
from shopping_assistant.config import load_config
from shopping_assistant.external.ecom_api_client.client import (
    EcomAPIClient,
)
from shopping_assistant.external.ecom_api_client.credentials import (
    Credentials,
)
from shopping_assistant.graph.types import State
from shopping_assistant.tools.cart_actions import Cart

load_dotenv("../.env")
config = load_config()

ecom_api_client = EcomAPIClient(
    base_url=os.getenv("ECOM_API_BASE_URL"),
    credentials=Credentials(user_id=1),
)

cart = Cart(api_client=ecom_api_client)

seed_products = {
    "southwest-bracelet": 1,
    "floral-choker-necklace": 2,
    "ivy-leaf-embroidered-skirt": 1,
}
cart.empty_cart()

for product_slug, quantity in seed_products.items():
    cart.add_item(product_slug=product_slug, quantity=quantity)

agent = ShoppingActionsAgent(config=config["agents"]["shopping_actions"], cart=cart)

queries = [
    "Add trendy-tapered-sunglasses to my cart",
    "Can I please see my cart?",
    "Update the quantity of southwest-bracelet to 2",
    "Remove all bracelets from my cart",
]


async def main():
    for query in queries:
        state = State(messages=[{"role": "user", "content": query}])
        new_state = await agent.run(state)
        print(f"User  : {query!r}")
        print(new_state.messages[-1]["content"])
        print()


asyncio.run(main())

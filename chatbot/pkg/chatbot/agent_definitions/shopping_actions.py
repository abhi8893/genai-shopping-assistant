# from collections import Counter
from chatbot.graph.types import State
from agents import Agent, Runner
from agents import FunctionTool, function_tool
from typing import Annotated
from chatbot.tools.cart_actions import Cart


class ShoppingActionsAgent:
    name: str = "shopping_actions"
    alias: str = "Shopping Actions"

    def __init__(self, config, cart: Cart):
        self.config = config
        self.cart = cart
        self.tool_store = self._get_tool_store()
        self.agent_actions = self._define_agent_actions(self.tool_store)
        self.action_list = self._get_action_list(self.agent_actions)
        self.action_summary = self._get_action_summary(self.agent_actions)
        self.action_detailed = self._get_action_detailed(
            self.action_summary, self.agent_actions
        )
        self.system_prompt = self._build_system_prompt(
            self.action_list, self.action_summary, self.action_detailed
        )
        self.agent = self._build_agent(self.system_prompt)

    def _get_tool_store(self) -> dict[str, list[FunctionTool]]:
        return {
            "cart": self._get_cart_action_tools(),
        }

    @property
    def tools(self):
        tools = []
        for action, tool_lst in self.tool_store.items():
            tools += tool_lst

        return tools

    def _get_cart_action_tools(self) -> list[FunctionTool]:
        @function_tool
        def add_to_cart(
            product_slug: Annotated[str, "product_slug"],
            quantity: Annotated[int, "quantity"] = 1,
        ) -> dict:
            """Add a product to user's cart"""
            try:
                self.cart.add_item(product_slug, quantity)
            except Exception as e:
                return "Error updating cart: " + str(e)

            return f"Cart updated successfully. Current Cart: {self.cart.view_cart()}"

        @function_tool
        def remove_from_cart(
            product_slug: Annotated[str, "product_slug"],
            quantity: Annotated[int, "quantity"] = 1,
        ) -> dict:
            """Remove a product from user's cart. Returns the updated cart."""
            self.cart.remove_item(product_slug, quantity)
            return f"Cart updated successfully. Current Cart: {self.cart.view_cart()}"

        @function_tool
        def view_cart() -> dict:
            """View user's cart"""
            return self.cart.view_cart()

        @function_tool
        def empty_cart() -> str:
            """Empty user's cart"""
            self.cart.empty_cart()
            return f"Cart updated successfully. Current Cart: {self.cart.view_cart()}"

        @function_tool
        def empty_item_from_cart(product_slug: Annotated[str, "product_slug"]) -> str:
            """Empty a specific item from user's cart"""
            self.cart.empty_item(product_slug)
            return f"Cart updated successfully. Current Cart: {self.cart.view_cart()}"

        return [
            add_to_cart,
            remove_from_cart,
            view_cart,
            empty_cart,
            empty_item_from_cart,
        ]

    def _define_agent_actions(self, tool_store: dict[str, list[FunctionTool]]) -> dict:
        agent_actions = {
            "cart": {
                "summary": "Manage your shopping cart (add or remove items, view cart)",
                "tools": tool_store["cart"],
            }
        }

        return agent_actions

    def _get_action_list(self, agent_actions: dict) -> list[str]:
        return list(agent_actions.keys())

    def _get_action_summary(self, agent_actions: dict) -> dict[str, str]:
        action_summary = {
            action_type: f"{idx + 1}. Action=`{action_type}`: {info['summary']}"
            for idx, (action_type, info) in enumerate(agent_actions.items())
        }

        return action_summary

    def _get_action_detailed(
        self, action_summary: dict[str, str], agent_actions: dict
    ) -> dict[str, str]:
        action_detailed = ""
        for idx, (action_type, info) in enumerate(agent_actions.items()):
            action_detailed += action_summary[action_type] + "\n"
            for tool in info["tools"]:
                action_detailed += f"- Tool=`{tool.name}`: {tool.description}" + "\n"

        return action_detailed

    def _build_system_prompt(
        self,
        action_list: list[str],
        action_summary: dict[str, str],
        action_detailed: dict[str, str],
    ) -> str:
        system_prompt = self.config["prompts"]["system_prompt"].format(
            action_list=action_list,
            action_summary="\n".join(action_summary.values()),
            action_detailed=action_detailed,
        )

        return system_prompt

    def _build_agent(self, system_prompt: str) -> Agent:
        return Agent(
            name=self.name,
            instructions=system_prompt,
            tools=self.tools,
            model=self.config["llm"],
        )

    async def run(self, state: State) -> State:
        response = await Runner.run(self.agent, state.messages)
        new_state = State(
            messages=[
                {
                    "role": "assistant",
                    "content": f"{self.alias} Agent: {response.final_output}",
                }
            ],
            prev_recommended_products=state.prev_recommended_products,
            last_response_agent=self.name,
        )
        return new_state

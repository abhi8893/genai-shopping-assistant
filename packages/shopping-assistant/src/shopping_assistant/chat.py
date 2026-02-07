try:
    from langfuse.openai import openai
except ImportError:
    import openai

import gradio as gr
from langchain_core.runnables import RunnableConfig
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
from langgraph.checkpoint.memory import InMemorySaver
from weaviate import WeaviateClient

from shopping_assistant.agent_definitions import (
    CustomerServiceAgent,
    ProductSearchAgent,
    RouterAgent,
    ShoppingActionsAgent,
)
from shopping_assistant.external.ecom_api_client.client import EcomAPIClient
from shopping_assistant.external.ecom_api_client.credentials import (
    Credentials as EcomAPICredentials,
)
from shopping_assistant.graph.graph import build_graph
from shopping_assistant.graph.types import State
from shopping_assistant.tools.cart_actions import Cart


class Chat:
    def __init__(
        self,
        config: dict,
        ecom_api_client: EcomAPIClient = None,
        openai_client: openai.OpenAI = None,
        weaviate_client: WeaviateClient = None,
        langfuse_client: Langfuse = None,
    ):
        self.config = config
        self.ecom_api_client = (
            ecom_api_client
            if ecom_api_client is not None
            else EcomAPIClient(base_url="http://localhost:8000/api/v1")
        )
        self.openai_client = openai.OpenAI() if openai_client is None else openai_client
        self.weaviate_client = weaviate_client
        self.langfuse_client = langfuse_client

        self.cart = self._fetch_cart()
        self.agents = self._initialize_agents(cart=self.cart)
        self.memory = self._initialize_memory()
        self.graph = self._build_graph(agents=self.agents, memory=self.memory)
        self.set_thread("1")

    def set_thread(self, thread_id: str):
        self.thread_id = thread_id

    @property
    def run_config(self) -> RunnableConfig:
        base_conf = {
            "configurable": {"thread_id": self.thread_id},
        }

        if self.langfuse_client is not None:  # noqa: SIM102
            # TODO: Does this cause additional network I/O? Or can
            # LangfuseCallbackHandler gracefully fail if Langfuse is not available?
            if self.langfuse_client.auth_check():
                base_conf["callbacks"] = [LangfuseCallbackHandler()]
        return base_conf

    async def query(self, query: str) -> str:
        state = State(messages=[{"role": "user", "content": query}])
        new_state = await self.graph.ainvoke(state, self.run_config)

        return new_state["messages"][-1]["content"]

    async def cli_chat(self, print_user_input: bool = False) -> str:
        while True:
            user_input = input("User: ")
            if print_user_input:
                print("User: " + user_input)
            if user_input == "exit":
                print("Assistant: Goodbye!")
                return

            state = State(messages=[{"role": "user", "content": user_input}])
            new_state = await self.graph.ainvoke(state, self.run_config)

            print(new_state["messages"][-1]["content"])

    def web_ui_chat(self):
        async def chat(user_input: str, history):  # noqa: ARG001
            message = {"role": "user", "content": user_input}

            response = await self.graph.ainvoke(
                State(messages=[message]), self.run_config
            )

            return response["messages"][-1]["content"]

        return gr.ChatInterface(
            fn=chat,
            title="Shopping Assistant",
        ).launch()

    def _fetch_cart(self) -> Cart:
        return Cart(api_client=self.ecom_api_client)

    def _initialize_agents(self, cart: Cart) -> dict:
        agents = {}

        agents["router"] = RouterAgent(
            self.config["agents"]["router"], openai_client=self.openai_client
        )
        agents["shopping_actions"] = ShoppingActionsAgent(
            self.config["agents"]["shopping_actions"], cart=cart
        )
        agents["product_search"] = ProductSearchAgent(
            self.config["agents"]["product_search"],
            openai_client=self.openai_client,
            weaviate_client=self.weaviate_client,
            langfuse_client=self.langfuse_client,
        )
        agents["customer_service"] = CustomerServiceAgent(
            self.config["agents"]["customer_service"], openai_client=self.openai_client
        )

        return agents

    def _initialize_memory(self):
        return InMemorySaver()

    def _build_graph(self, agents: dict, memory: InMemorySaver):
        return build_graph(
            router_agent=agents["router"],
            shopping_actions_agent=agents["shopping_actions"],
            customer_service_agent=agents["customer_service"],
            product_search_agent=agents["product_search"],
            memory=memory,
        )


if __name__ == "__main__":
    import asyncio

    from agents import set_tracing_disabled

    from shopping_assistant.config import load_config
    from shopping_assistant.env import load_env

    set_tracing_disabled(True)
    load_env(
        "~/personal/projects/ecom-shopping-assistant/genai-shopping-assistant/.env"
    )
    workflow_config = load_config(
        "~/personal/projects/ecom-shopping-assistant/genai-shopping-assistant/chatbot/conf/config.yml"
    )

    chat = Chat(
        ecom_api_client=EcomAPIClient(
            base_url="http://localhost:8000/api/v1",
            credentials=EcomAPICredentials(user_id=1),
        ),
        config=workflow_config,
    )
    asyncio.run(chat.cli_chat())
    # chat.web_ui_chat()

try:
    from langfuse.openai import openai
except ImportError:
    import openai

from shopping_assistant.graph.types import State


class CustomerServiceAgent:
    name: str = "customer_service"
    alias: str = "Customer Service"

    def __init__(self, config, openai_client: openai.OpenAI = None):
        self.config = config
        self.openai_client = openai.OpenAI() if openai_client is None else openai_client

    def run(self, state: State) -> State:
        input_messages = [
            {"role": "system", "content": self.config["prompts"]["system_prompt"]},
            *state.messages[:-1],
            {"role": "user", "content": state.messages[-1]["content"]},
        ]

        responses_obj = self.openai_client.chat.completions.create(
            model=self.config["llm"], messages=input_messages
        )

        response = {
            "role": "assistant",
            "content": f"{self.alias} Agent: {responses_obj.choices[0].message.content}",
        }

        new_state = State(
            messages=[response],
            prev_recommended_products=state.prev_recommended_products,
            last_response_agent=self.name,
        )

        return new_state

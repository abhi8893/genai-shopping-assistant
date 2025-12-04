from typing import Literal
from pydantic import BaseModel
import chatbot.config as module_config
import openai
from chatbot.graph.types import State

class DownstreamRoutesAgentResponse(BaseModel):
    route: Literal[*module_config.DOWNSTREAM_ROUTES]


class RouterAgent:

    def __init__(self, config, openai_client: openai.OpenAI = None):
        self._validate_config(config)
        self.config = config
        self.openai_client = openai.OpenAI() if openai_client is None else openai_client

    @staticmethod
    def _validate_config(config):
        downstream_routes_in_config = [d["name"] for d in config['downstream_routes']]
        assert set(downstream_routes_in_config) == set(module_config.DOWNSTREAM_ROUTES), "Downstream routes in package config do not match downstream routes in the passed config"


    def run(self, state: State) -> Literal[*module_config.DOWNSTREAM_ROUTES]:
        input_messages = [
            {"role": "system", "content": self.config['prompts']['system_prompt']},
            *state.messages[:-1],
            {"role": "user", "content": f"Route based on this message: {state.messages[-1]['content']}"}
        ]

        response = self.openai_client.responses.parse(
            model=self.config["llm"],
            input=input_messages,
            text_format=DownstreamRoutesAgentResponse
        )

        return response.output_parsed.route

        
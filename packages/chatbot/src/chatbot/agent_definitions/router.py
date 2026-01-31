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

        self.system_prompt = self._get_system_prompt()

    @staticmethod
    def _validate_config(config):
        downstream_routes_in_config = [d["name"] for d in config["downstream_routes"]]
        assert set(downstream_routes_in_config) == set(
            module_config.DOWNSTREAM_ROUTES
        ), (
            "Downstream routes in package config do not match downstream routes in the passed config"
        )

    @staticmethod
    def _get_downstream_routes_description_for_prompt(downstream_routes):
        routes_lst = [d["name"] for d in downstream_routes]
        desc = f"The available downstream routes are: {routes_lst}"
        desc += "\n\n"

        for idx, route in enumerate(downstream_routes):
            desc += f"\n(Route {idx + 1}) `{route['name']}`: {route['description']}"
            desc += "\nExamples:"
            for idx, example in enumerate(route["examples"]):
                desc += f"\n{idx + 1}: {example}"

            desc += "\n\n"

        desc += "\n\n"
        return desc

    def _get_system_prompt(self):
        downstream_routes_desc = self._get_downstream_routes_description_for_prompt(
            self.config["downstream_routes"]
        )
        system_prompt = self.config["prompts"]["system_prompt"].format(
            downstream_routes_desc=downstream_routes_desc
        )
        return system_prompt

    def run(self, state: State) -> Literal[*module_config.DOWNSTREAM_ROUTES]:
        input_messages = [
            {"role": "system", "content": self.system_prompt},
            *state.messages[:-1],
            {
                "role": "user",
                "content": f"Route based on this message: {state.messages[-1]['content']}",
            },
        ]

        response = self.openai_client.chat.completions.parse(
            model=self.config["llm"],
            messages=input_messages,
            response_format=DownstreamRoutesAgentResponse,
        )

        return response.choices[0].message.parsed.route

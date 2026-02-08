from typing import Annotated

from pydantic import BaseModel, Field

import shopping_assistant.config as module_config
from shopping_assistant.graph.utils import add_messages_openai
from shopping_assistant.types import ProductVectorDBRecord


class State(BaseModel):
    messages: Annotated[list, add_messages_openai]
    prev_recommended_products: list[ProductVectorDBRecord] | None = None
    last_response_agent: str | None = Field(
        default=None, choices=module_config.DOWNSTREAM_ROUTES, optional=True
    )

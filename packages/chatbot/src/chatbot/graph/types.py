from pydantic import BaseModel, Field
from typing import Annotated
from chatbot.graph.utils import add_messages_openai
import chatbot.config as module_config
from chatbot.types import ProductVectorDBRecord


class State(BaseModel):
    messages: Annotated[list, add_messages_openai]
    prev_recommended_products: list[ProductVectorDBRecord] | None = None
    last_response_agent: str | None = Field(
        default=None, choices=module_config.DOWNSTREAM_ROUTES, optional=True
    )

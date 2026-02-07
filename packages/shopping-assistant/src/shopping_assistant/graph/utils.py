import contextlib

from langchain_community.adapters.openai import (
    convert_message_to_dict as convert_lc_message_to_openai_dict,
)
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


def add_messages_openai(
    messages_l: list[BaseMessage] | list[dict],
    messages_r: list[BaseMessage] | list[dict],
) -> list[dict]:
    messages_comb = add_messages(messages_l, messages_r)

    for idx, msg in enumerate(messages_comb):
        # TODO: Consider handling better vs suppressing
        with contextlib.suppress(TypeError):
            messages_comb[idx] = convert_lc_message_to_openai_dict(msg)

    return messages_comb

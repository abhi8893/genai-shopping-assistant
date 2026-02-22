import base64
import logging
import os

import httpx
import logfire
from langfuse import Langfuse
from langfuse import get_client as get_langfuse_client


def langfuse_auth_check(langfuse: Langfuse) -> bool:
    try:
        auth_check = langfuse.auth_check()
        logging.info("Langfuse authentication check: %s", auth_check)
        return auth_check
    except httpx.ConnectError as exc:
        logging.error("Error checking Langfuse authentication: %s", exc)
        return False


def configure_langfuse() -> Langfuse:
    # from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor

    langfuse_public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key = os.environ.get("LANGFUSE_SECRET_KEY")

    langfuse_auth = base64.b64encode(
        f"{langfuse_public_key}:{langfuse_secret_key}".encode()
    ).decode()

    # Configure OpenTelemetry endpoint & headers
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = (
        os.environ.get("LANGFUSE_BASE_URL") + "/api/public/otel"
    )
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {langfuse_auth}"

    langfuse = get_langfuse_client()

    # BUG: logging doesn't show up
    if langfuse_auth_check(langfuse):
        logging.info("Langfuse authentication successful")
    else:
        logging.warning("Langfuse authentication failed")

    # TODO: Should this be done only when langfuse authentication is successful?
    # Configure logfire instrumentation.
    logfire.configure(
        service_name="my_agent_service",
        send_to_logfire=False,
    )
    # This method automatically patches the OpenAI Agents SDK to
    # send logs via OTLP to Langfuse.
    logfire.instrument_openai_agents()

    # NOTE: Disabled because logfire instrumentation method for openai agents
    # (more fields visible in langfuse UI).
    # OpenAIAgentsInstrumentor().instrument()

    return langfuse

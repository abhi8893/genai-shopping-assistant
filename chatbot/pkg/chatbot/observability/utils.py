
import base64
from langfuse import Langfuse
from langfuse import get_client as get_langfuse_client
import os
import logging
import logfire


def configure_langfuse() -> Langfuse:
    # from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
    
    LANGFUSE_AUTH = base64.b64encode(
        f"{os.environ.get('LANGFUSE_PUBLIC_KEY')}:{os.environ.get('LANGFUSE_SECRET_KEY')}".encode()
    ).decode()
 
    # Configure OpenTelemetry endpoint & headers
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = os.environ.get("LANGFUSE_BASE_URL") + "/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

    langfuse = get_langfuse_client()

    # BUG: logging doesn't show up
    if langfuse.auth_check():
        logging.info("Langfuse authentication successful")
    else:
        logging.warning("Langfuse authentication failed")

    
    # TODO: Should this be done only when langfuse authentication is successful?
    # Configure logfire instrumentation.
    logfire.configure(
        service_name='my_agent_service',
        send_to_logfire=False,
    )
    # This method automatically patches the OpenAI Agents SDK to send logs via OTLP to Langfuse.
    logfire.instrument_openai_agents()
    
    # NOTE: Disabled because logfire instrumentation method for openai agents is better somehow (more fields visible in langfuse UI).
    # OpenAIAgentsInstrumentor().instrument()

    return langfuse

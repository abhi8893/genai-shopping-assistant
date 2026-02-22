import logging
import os

import httpx


def langfuse_auth_check_preflight() -> bool:
    host = os.getenv("LANGFUSE_HOST")
    public = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret = os.getenv("LANGFUSE_SECRET_KEY")

    if not host or not public or not secret:
        return False

    try:
        r = httpx.get(
            f"{host}/api/public/projects",
            auth=(public, secret),
            timeout=2,
        )
        return r.status_code == httpx.codes.OK

    except Exception:
        return False


# TODO: Add option of which loggers to set to CRITICAL level
def setup_opentelemetry_logging():
    """
    Disable verbose opentelemetry logs.
    """
    for name in [
        "opentelemetry.sdk._shared_internal",
        "opentelemetry.exporter.otlp",
        "opentelemetry.sdk.trace.export",
    ]:
        logging.getLogger(name).setLevel(logging.CRITICAL)

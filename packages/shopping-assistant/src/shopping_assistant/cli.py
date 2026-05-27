import asyncio
import logging
import os
from importlib.resources import files
from pathlib import Path

import click
import weaviate

from shopping_assistant.chat import Chat
from shopping_assistant.config import CONFIG_FILE_PATH, load_config
from shopping_assistant.env import load_env
from shopping_assistant.external.ecom_api_client.client import EcomAPIClient
from shopping_assistant.external.ecom_api_client.credentials import (
    Credentials as EcomAPICredentials,
)
from shopping_assistant.observability.utils import configure_langfuse

logger = logging.getLogger(__name__)

DEFAULT_DIR = ".shopping-assistant"
_PACKAGE_DATA = files("shopping_assistant")


@click.group()
def main():
    """GenAI Shopping Assistant CLI."""


@main.group()
def create():
    """Scaffold a new project."""


@create.command("new")
@click.argument("out_dir", default=DEFAULT_DIR)
def create_new(out_dir):
    """Create a new shopping assistant project directory.

    OUT_DIR is the target directory (default: .shopping-assistant).
    """
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy config/config.yml from package data
    config_dir = target_dir / "config"
    config_dir.mkdir(exist_ok=True)

    src_config = _PACKAGE_DATA / "config" / "config.yml"
    dst_config = config_dir / "config.yml"
    dst_config.write_bytes(src_config.read_bytes())

    # Copy .env.example from package data
    src_env = _PACKAGE_DATA / ".env.example"
    dst_env = target_dir / ".env.example"
    dst_env.write_bytes(src_env.read_bytes())

    click.echo(f"Created new shopping assistant project in '{target_dir}'")
    click.echo(f"  {dst_config}")
    click.echo(f"  {dst_env}")


@main.command("chat")
@click.option("--user-id", required=True, help="User identifier.")
@click.option("--mode", default="cli", help="Mode to run in (cli or web).")
@click.option(
    "--config-dir",
    default=None,
    help=(
        "Path to config directory containing config.yml (default: package data config)."
    ),
)
@click.option(
    "--env-file",
    default=None,
    help="Path to .env file (default: assumes environment variables are set).",
)
def chat(user_id, mode, config_dir, env_file):
    """Start an interactive chat session."""
    # Load env file
    if env_file:
        load_env(env_file)
    else:
        logging.warning(
            "No --env-file provided. Assuming environment variables are already set."
        )

    # Load config
    if config_dir:
        config_path = Path(config_dir) / "config.yml"
    else:
        config_path = CONFIG_FILE_PATH
        logging.warning(
            "No --config-dir provided. Using package default config: %s", config_path
        )

    config = load_config(str(config_path))

    # Initialize Weaviate client
    weaviate_connection_params = weaviate.connect.ConnectionParams(
        http={
            "host": os.getenv("WEAVIATE_HTTP_HOST"),
            "port": os.getenv("WEAVIATE_HTTP_PORT"),
            "secure": os.getenv("WEAVIATE_HTTP_SECURE"),
        },
        grpc={
            "host": os.getenv("WEAVIATE_GRPC_HOST"),
            "port": os.getenv("WEAVIATE_GRPC_PORT"),
            "secure": os.getenv("WEAVIATE_GRPC_SECURE"),
        },
    )

    weaviate_client = weaviate.WeaviateClient(
        connection_params=weaviate_connection_params
    )

    ecom_api_base_url = os.getenv("ECOM_API_BASE_URL")
    ecom_api_client = EcomAPIClient(
        base_url=ecom_api_base_url,
        credentials=EcomAPICredentials(user_id=user_id),
    )

    langfuse_client = configure_langfuse()

    chat_session = Chat(
        config=config,
        weaviate_client=weaviate_client,
        ecom_api_client=ecom_api_client,
        langfuse_client=langfuse_client,
    )

    if mode == "cli":
        asyncio.run(chat_session.cli_chat())
    elif mode == "web":
        chat_session.web_ui_chat()


if __name__ == "__main__":
    main()

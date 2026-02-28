import os

import weaviate
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shopping_assistant.chat import Chat
from shopping_assistant.config import load_config
from shopping_assistant.external.ecom_api_client.client import EcomAPIClient
from shopping_assistant.external.ecom_api_client.credentials import (
    Credentials as EcomAPICredentials,
)
from shopping_assistant.observability.preflight import setup_opentelemetry_logging
from shopping_assistant.observability.utils import configure_langfuse

# TODO: Do this based on DEV, STAGING, PROD env (in DEV we want to see all logs)
setup_opentelemetry_logging()

VERSION = "0.1.0"

app = FastAPI(
    title="Shopping Assistant Chatbot API",
    description=(
        "A shopping assistant chatbot that uses GenAI to help customers "
        "find products they are looking for."
    ),
    version=VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHATS = {}
CONF_PATH = ".shopping-assistant/config/config.yml"

CONFIG = load_config(CONF_PATH)
ECOM_API_BASE_URL = os.getenv("ECOM_API_BASE_URL", "http://localhost:8000/api/v1")


def initialize_chat(user_id: str, thread_id: str):
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

    chat_id = (user_id, thread_id)

    ecom_api_client = EcomAPIClient(
        base_url=ECOM_API_BASE_URL, credentials=EcomAPICredentials(user_id=user_id)
    )

    langfuse_client = configure_langfuse()

    CHATS[chat_id] = Chat(
        config=CONFIG,
        weaviate_client=weaviate_client,
        ecom_api_client=ecom_api_client,
        langfuse_client=langfuse_client,
    )
    CHATS[chat_id].set_thread(thread_id)


class Request(BaseModel):
    user_id: str
    query: str
    thread_id: str


@app.post("/chat")
async def chat(request: Request):
    chat_id = (request.user_id, request.thread_id)
    chat = CHATS.get(chat_id)
    if not chat:
        initialize_chat(request.user_id, request.thread_id)

    chat = CHATS[chat_id]

    response = await chat.query(request.query)
    return {"response": response}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "message": "Shopping Assistant Chatbot API",
        "version": VERSION,
        "endpoints": {
            "/chat": "Chat with the chatbot",
            "/health": "Check if the API is healthy",
        },
    }

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot.chat import Chat
from chatbot.config import load_config
from chatbot.env import load_env
import weaviate
import os


VERSION = "0.1.0"

app = FastAPI(
    title="Chatbot API",
    description="A shopping assistant chatbot that uses GenAI to help customers find products they are looking for.",
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
CONF_PATH = "../conf/config.yml"

CONFIG = load_config(CONF_PATH)


def initialize_chat(user_id: str):
    weaviate_connection_params = weaviate.connect.ConnectionParams(
        http={
            "host": os.getenv("WEAVIATE_HTTP_HOST"),
            "port": os.getenv("WEAVIATE_HTTP_PORT"),
            "secure": os.getenv("WEAVIATE_HTTP_SECURE")
        },
        grpc={
            "host": os.getenv("WEAVIATE_GRPC_HOST"),
            "port": os.getenv("WEAVIATE_GRPC_PORT"),
            "secure": os.getenv("WEAVIATE_GRPC_SECURE")
        }
    )

    weaviate_client = weaviate.WeaviateClient(
        connection_params=weaviate_connection_params
    )

    CHATS[user_id] = Chat(
        user_id=user_id,
        config=CONFIG,
        weaviate_client=weaviate_client
    )


class Request(BaseModel):
    user_id: str
    query: str
    thread_id: str

@app.post("/chat")
async def chat(request: Request):
    chat = CHATS.get(request.user_id)
    if not chat:
        initialize_chat(request.user_id)

    chat = CHATS[request.user_id]
    chat.set_thread(request.thread_id)
    
    response = await chat.query(request.query)
    return {"response": response}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "message": "Chatbot API",
        "version": VERSION,
        "endpoints": {
            "/chat": "Chat with the chatbot",
            "/health": "Check if the API is healthy"
        }
    }
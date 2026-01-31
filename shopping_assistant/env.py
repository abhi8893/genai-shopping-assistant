from dotenv import load_dotenv
from shopping_assistant.constants import PROJECT_ROOT
from pathlib import Path

ENV_VARS_FILE_PATH = Path(PROJECT_ROOT) / ".env"


def load_env():
    return load_dotenv(ENV_VARS_FILE_PATH, override=True)

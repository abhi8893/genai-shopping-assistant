
from dotenv import load_dotenv
from pathlib import Path
from chatbot.constants import PROJECT_ROOT

ENV_VARS_FILE_PATH = Path(PROJECT_ROOT) / ".env"

def load_env(fpath: str = ENV_VARS_FILE_PATH):
    fpath = Path(fpath).expanduser()
    return load_dotenv(fpath, override=True)
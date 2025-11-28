from chatbot.constants import PROJECT_ROOT
import yaml
from pathlib import Path

CONFIG_FILE_PATH =  Path(PROJECT_ROOT) / "conf/config.yml"

DOWNSTREAM_ROUTES = [
    "product_search",
    "shopping_actions",
    "customer_service"
]

def load_config(fpath: str = CONFIG_FILE_PATH):
    with open(fpath, "r") as f:
        conf = yaml.safe_load(f)

    return conf
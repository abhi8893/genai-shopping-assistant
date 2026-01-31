from chatbot.constants import PROJECT_ROOT
import yaml
from pathlib import Path

# TODO:
# Make a distinction between installation package and framework
# The config path specification should be part of the project / folder structure
# created with the framework capabilities of the package but NOT part of the package itself
# So something like chatbot create project <project_name> <project_dir> <args>
CONFIG_FILE_PATH = Path(PROJECT_ROOT) / "conf/config.yml"

DOWNSTREAM_ROUTES = ["product_search", "shopping_actions", "customer_service"]


def load_config(fpath: str = CONFIG_FILE_PATH):
    fpath = Path(fpath).expanduser()
    with open(fpath, "r") as f:
        conf = yaml.safe_load(f)

    return conf

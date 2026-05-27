import argparse
import logging
import os
from pathlib import Path

import pandas as pd
import sqlalchemy
import weaviate
import weaviate.classes as wvc
from dotenv import load_dotenv
from shopping_assistant.product_retrieval import WeaviateConnectionManager

VECTOR_DB_COLLECTION_NAME = "products"
OLLAMA_API_ENDPOINT = "http://ollama:11434"
EMBEDDING_MODEL = "nomic-embed-text"
WEAVIATE_INGESTION_BATCH_SIZE = 20
PRODUCT_DATA_FIELDS = [
    "product_id",
    "name",
    "slug",
    "description",
    "price",
    "created_at",
    "category_name",
    "subcategory_name",
    "category_slug",
    "subcategory_slug",
]
EMBEDDING_FIELDS = ["name", "description", "category_name", "subcategory_name"]
ECOM_BACKEND_DB_SQLITE_PATH = "services/ecom-backend/ecom_backend.db"

CUR_SCRIPT_REPO_ROOT_DEPTH = 3
REPO_ROOT = Path(__file__).parents[CUR_SCRIPT_REPO_ROOT_DEPTH]

WEAVIATE_ARG_NAMES = [
    "weaviate_http_host",
    "weaviate_http_port",
    "weaviate_http_secure",
    "weaviate_grpc_host",
    "weaviate_grpc_port",
    "weaviate_grpc_secure",
]

INCONSISTENT_WEAVIATE_ARGS_WARNING = (
    "Weaviate arguments are currently not recommended for use with this script."
    "Either all Weaviate arguments should be provided or none."
    "Alternatively, please ensure the environment variables are set correctly set in %s"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--ecom-backend-db-sqlite-path",
    default=ECOM_BACKEND_DB_SQLITE_PATH,
)
parser.add_argument("--vector-db-collection-name", default=VECTOR_DB_COLLECTION_NAME)
parser.add_argument("--ollama-api-endpoint", default=OLLAMA_API_ENDPOINT)
parser.add_argument("--embedding-model", default=EMBEDDING_MODEL)
parser.add_argument(
    "--weaviate-ingestion-batch-size", default=WEAVIATE_INGESTION_BATCH_SIZE
)
parser.add_argument("--weaviate-http-host", default=os.getenv("WEAVIATE_HTTP_HOST"))
parser.add_argument("--weaviate-http-port", default=os.getenv("WEAVIATE_HTTP_PORT"))
parser.add_argument("--weaviate-http-secure", default=os.getenv("WEAVIATE_HTTP_SECURE"))
parser.add_argument("--weaviate-grpc-host", default=os.getenv("WEAVIATE_GRPC_HOST"))
parser.add_argument("--weaviate-grpc-port", default=os.getenv("WEAVIATE_GRPC_PORT"))
parser.add_argument("--weaviate-grpc-secure", default=os.getenv("WEAVIATE_GRPC_SECURE"))
parser.add_argument("--env", default="dev", choices=["dev", "prod"])


# parse args
args = parser.parse_args()

app_env = args.env

if app_env == "prod":
    app_env_files = [
        str(REPO_ROOT / "platform/app/.env"),
    ]
elif app_env == "dev":
    app_env_files = [
        str(REPO_ROOT / "platform/app/.env"),
        str(REPO_ROOT / "platform/app/.env.dev"),
    ]


# Add warning for setting weaviate host and port
logger.warning(
    "WEAVIATE_HTTP_HOST, WEAVIATE_GRPC_HOST will be set to localhost",
)

# Add warning if weaviate arguments are passed

weaviate_args = {arg_name: getattr(args, arg_name) for arg_name in WEAVIATE_ARG_NAMES}
if any(weaviate_args.values()) and not all(weaviate_args.values()):
    logger.error(
        INCONSISTENT_WEAVIATE_ARGS_WARNING,
        app_env_files,
    )
    raise ValueError("Inconsistent Weaviate arguments provided")

if not all(weaviate_args.values()):
    logger.warning(
        "Loading Weaviate arguments from environment file: %s",
        app_env_files,
    )
    for env_file in app_env_files:
        load_dotenv(env_file)

    try:
        weaviate_args = {
            arg_name: os.environ[arg_name.upper()] for arg_name in WEAVIATE_ARG_NAMES
        }
        weaviate_args["weaviate_http_host"] = "localhost"
        weaviate_args["weaviate_grpc_host"] = "localhost"
    except KeyError as e:
        logger.error(
            "Missing Weaviate argument in environment file: %s",
            e,
        )
        raise ValueError(f"Missing Weaviate argument in environment file: {e}") from e


print(weaviate_args)


# connect to ecom backend db
ecom_backend_db_sqlite_path = str(REPO_ROOT / args.ecom_backend_db_sqlite_path)
if not os.path.exists(ecom_backend_db_sqlite_path):
    raise FileNotFoundError(
        f"Ecom Backend SQLite database {ecom_backend_db_sqlite_path} does not exist"
    )

engine = sqlalchemy.create_engine(f"sqlite:///{ecom_backend_db_sqlite_path}")

with engine.connect() as conn:
    df = pd.read_sql(
        """
        SELECT
            prod.*,
            prod_h.category_name,
            prod_h.subcategory_name,
            prod_h.category_slug,
            prod_h.subcategory_slug

        FROM product prod
        JOIN product_hierarchy prod_h
        ON (prod_h.category_id = prod.category_id)
        AND (prod_h.subcategory_id = prod.subcategory_id)
        """,
        conn,
    )

df = df.rename(columns={"id": "product_id"})

# connect to weaviate
weaviate_connection_params = weaviate.connect.ConnectionParams(
    http={
        "host": weaviate_args["weaviate_http_host"],
        "port": weaviate_args["weaviate_http_port"],
        "secure": weaviate_args["weaviate_http_secure"],
    },
    grpc={
        "host": weaviate_args["weaviate_grpc_host"],
        "port": weaviate_args["weaviate_grpc_port"],
        "secure": weaviate_args["weaviate_grpc_secure"],
    },
)

weaviate_client = weaviate.WeaviateClient(connection_params=weaviate_connection_params)


with WeaviateConnectionManager(client=weaviate_client) as weaviate_client_connected:
    logger.info("Deleting collection: %s", VECTOR_DB_COLLECTION_NAME)
    weaviate_client_connected.collections.delete(VECTOR_DB_COLLECTION_NAME)

    logger.info("Creating collection: %s", VECTOR_DB_COLLECTION_NAME)
    products = weaviate_client_connected.collections.create(
        name=VECTOR_DB_COLLECTION_NAME,
        vector_config=wvc.config.Configure.Vectors.text2vec_ollama(
            api_endpoint=args.ollama_api_endpoint,
            model=args.embedding_model,
            source_properties=EMBEDDING_FIELDS,
        ),
        properties=[
            wvc.config.Property(name="product_id", data_type=wvc.config.DataType.INT)
        ],
    )

    logger.info("Embedding fields set to %s", EMBEDDING_FIELDS)

    logger.info(
        "Ingesting %s records into collection: %s", len(df), VECTOR_DB_COLLECTION_NAME
    )
    with products.batch.fixed_size(batch_size=WEAVIATE_INGESTION_BATCH_SIZE) as batch:
        for _idx, row in df[PRODUCT_DATA_FIELDS].iterrows():
            rec = row.to_dict()
            batch.add_object(properties=rec)


logger.info(
    "Successfully ingested %s records into collection: %s",
    len(df),
    VECTOR_DB_COLLECTION_NAME,
)

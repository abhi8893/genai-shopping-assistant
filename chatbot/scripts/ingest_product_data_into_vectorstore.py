import argparse
import logging
import weaviate
import weaviate.classes as wvc
import os
import sqlalchemy
from chatbot.product_retrieval import WeaviateConnectionManager
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--sqlite-db-path")
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


# parse args
args = parser.parse_args()

# load data
if not os.path.exists(args.sqlite_db_path):
    raise FileNotFoundError(f"SQLite database {args.sqlite_db_path} does not exist")

engine = sqlalchemy.create_engine(f"sqlite:///{args.sqlite_db_path}")

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

# Create weaviate client
weaviate_connection_params = weaviate.connect.ConnectionParams(
    http={
        "host": args.weaviate_http_host,
        "port": args.weaviate_http_port,
        "secure": args.weaviate_http_secure,
    },
    grpc={
        "host": args.weaviate_grpc_host,
        "port": args.weaviate_grpc_port,
        "secure": args.weaviate_grpc_secure,
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
        for idx, row in df[PRODUCT_DATA_FIELDS].iterrows():
            rec = row.to_dict()
            batch.add_object(properties=rec)


logger.info(
    "Successfully ingested %s records into collection: %s",
    len(df),
    VECTOR_DB_COLLECTION_NAME,
)

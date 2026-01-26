from weaviate import WeaviateClient
import weaviate.classes as wvc
import functools
import weaviate
from langfuse import observe as langfuse_observe


class WeaviateConnectionManager:

    def __init__(self, client: WeaviateClient):
        self.client = client

    def __enter__(self) -> WeaviateClient:
        self.client.connect()
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    

def _retrieve_products_client(
    weaviate_client: WeaviateClient,
    filter_obj: wvc.query.Filter,
    query: str = None,
    n: int = 5,
):
    products = weaviate_client.collections.use("products")
    
    if not query:
        response = products.query.fetch_objects(filters=filter_obj, limit=n)
    else:
        response = products.query.near_text(
            query=query,
            filters=filter_obj,
            limit=n,
        )
    
    return response

@langfuse_observe(
    name="retrieve-products",
    as_type="retriever"
)
def retrieve_products(
    query: str = None,
    categories: list[str] = None,
    subcategories: list[str] = None,
    min_price: float = None,
    max_price: float = None,
    n: int = 5,
    weaviate_client: WeaviateClient = None,
):
    """
    Retrieve products from the catalog based on the given query and filters.
    """

    filters = []

    if categories:
        filters.append(
            wvc.query.Filter.by_property("category_slug").contains_any(categories)
        )

    if subcategories:
        filters.append(
            wvc.query.Filter.by_property("subcategory_slug").contains_any(subcategories)
        )

    if min_price:
        filters.append(
            wvc.query.Filter.by_property("price").greater_or_equal(min_price)
        )

    if max_price:
        filters.append(
            wvc.query.Filter.by_property("price").less_or_equal(max_price)
        )

    if filters:
        filter_obj = functools.reduce(
            lambda x, y: x & y,
            filters,
        )
    else:
        filter_obj = None

    if weaviate_client is None:
        with weaviate.connect_to_local() as weaviate_client:
            product_retrieval_response = _retrieve_products_client(
                weaviate_client=weaviate_client,
                filter_obj=filter_obj,
                query=query,
                n=n,
            )
    else:
        with WeaviateConnectionManager(weaviate_client) as weaviate_client_connected:
            product_retrieval_response = _retrieve_products_client(
                weaviate_client=weaviate_client_connected,
                filter_obj=filter_obj,
                query=query,
                n=n,
            )

    return product_retrieval_response

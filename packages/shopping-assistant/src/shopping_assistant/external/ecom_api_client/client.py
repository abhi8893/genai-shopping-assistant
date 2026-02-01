from shopping_assistant.external.ecom_api_client.resources.carts import CartsAPIClient
from shopping_assistant.external.ecom_api_client.resources.products import (
    ProductsAPIClient,
)
from shopping_assistant.external.ecom_api_client.credentials import Credentials


class EcomAPIClient:
    def __init__(self, base_url: str, credentials: Credentials = None):
        self.base_url = base_url
        self.carts = CartsAPIClient(base_url=base_url, credentials=credentials)
        self.products = ProductsAPIClient(base_url=base_url, credentials=credentials)

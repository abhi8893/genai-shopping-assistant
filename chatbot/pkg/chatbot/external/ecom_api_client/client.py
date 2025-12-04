from chatbot.external.ecom_api_client.resources.carts import CartsAPIClient
from chatbot.external.ecom_api_client.resources.products import ProductsAPIClient
from chatbot.external.ecom_api_client.credentials import Credentials

class EcomAPIClient:

    def __init__(self, base_url: str, credentials: Credentials):
        self.base_url = base_url
        self.carts = CartsAPIClient(base_url=base_url, credentials=credentials)
        self.products = ProductsAPIClient(base_url=base_url, credentials=credentials)

    
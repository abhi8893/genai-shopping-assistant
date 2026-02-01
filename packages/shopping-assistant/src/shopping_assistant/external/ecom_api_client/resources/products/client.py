from shopping_assistant.external.ecom_api_client.http import HttpClient
from shopping_assistant.external.ecom_api_client.credentials import Credentials
from shopping_assistant.external.ecom_api_client.resources.products.types import (
    ProductResponse,
)
from shopping_assistant.external.ecom_api_client.exceptions import (
    ApiError,
    ExceptionResponse,
)


class ProductsAPIClient:
    def __init__(self, base_url: str, credentials: Credentials = None):
        self.http = HttpClient(
            base_url=base_url, credentials=credentials, prefix="/products"
        )

    def get_all(
        self, page: int = 1, limit: int = 10
    ) -> list[ProductResponse] | ExceptionResponse:
        try:
            response = self.http.request(
                method="get",
                path="/",
                raise_error=True,
                params={"page": page, "limit": limit},
            )
            return [ProductResponse.model_validate(r) for r in response]
        except ApiError as e:
            return e.response

    def get_by_id(self, product_id: int) -> ProductResponse | ExceptionResponse:
        try:
            response = self.http.request(
                method="get", path=f"/id/{product_id}", raise_error=True
            )
            return ProductResponse.model_validate(response)
        except ApiError as e:
            return e.response

    def get_by_slug(self, product_slug: str) -> ProductResponse | ExceptionResponse:
        try:
            response = self.http.request(
                method="get", path=f"/slug/{product_slug}", raise_error=True
            )
            return ProductResponse.model_validate(response)
        except ApiError as e:
            return e.response

from shopping_assistant.external.ecom_api_client.http import HttpClient
from shopping_assistant.external.ecom_api_client.credentials import Credentials
from shopping_assistant.external.ecom_api_client.resources.carts.types import (
    CartCreateBody,
    CartResponse,
    CartUpdateBody,
)
from shopping_assistant.external.ecom_api_client.exceptions import (
    ApiError,
    ExceptionResponse,
)


# TODO: Handle exception handling result a lil more generically
class CartsAPIClient:
    def __init__(self, base_url: str, credentials: Credentials = None):
        self.base_url = base_url
        self.http = HttpClient(
            base_url=base_url, prefix="/carts", credentials=credentials
        )

    def get_all_carts(
        self, page: int = 1, limit: int = 10
    ) -> list[CartResponse] | ExceptionResponse:
        try:
            return [
                CartResponse.model_validate(c)
                for c in self.http.request(
                    "get", "/", raise_error=True, params={"page": page, "limit": limit}
                )
            ]
        except ApiError as e:
            return e.response

    def get_cart(self, cart_id: int) -> CartResponse | ExceptionResponse:
        try:
            return CartResponse.model_validate(
                self.http.request("get", f"/{cart_id}", raise_error=True)
            )
        except ApiError as e:
            return e.response

    def create_cart(
        self, cart_create_data: CartCreateBody
    ) -> CartResponse | ExceptionResponse:
        try:
            return CartResponse.model_validate(
                self.http.request(
                    "post", "/", json=cart_create_data.dict(), raise_error=True
                )
            )
        except ApiError as e:
            return e.response

    def delete_cart(self, cart_id: int) -> CartResponse | ExceptionResponse:
        try:
            return CartResponse.model_validate(
                self.http.request("delete", f"/{cart_id}", raise_error=True)
            )
        except ApiError as e:
            return e.response

    def update_cart(
        self, cart_id: int, cart_update_data: CartUpdateBody
    ) -> CartResponse | ExceptionResponse:
        try:
            return CartResponse.model_validate(
                self.http.request(
                    "put", f"/{cart_id}", json=cart_update_data.dict(), raise_error=True
                )
            )
        except ApiError as e:
            return e.response

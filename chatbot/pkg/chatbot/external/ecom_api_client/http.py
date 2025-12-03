import requests
from chatbot.external.ecom_api_client.credentials import Credentials
from chatbot.external.ecom_api_client.exceptions import ApiError, ExceptionResponse
import pydantic

class HttpClient:

    def __init__(self, base_url: str, credentials: Credentials | None = None, prefix=""):
        self.base_url = base_url + prefix
        self.session = requests.Session()
        self.credentials = credentials


    def request(self, method, path, raise_error=False, **kwargs) -> dict | ExceptionResponse:

        # TODO: Temp measure before I implement better auth in API
        headers = kwargs.pop("headers", {})
        if self.credentials:
            headers["X-User-Id"] = str(self.credentials.user_id)

        response_obj = self.session.request(
            method=method,
            url=self.base_url + path,
            headers=headers,
            **kwargs
        )

        response_json = response_obj.json()

        if isinstance(response_json, dict):
            # TODO: Temp way of differentiating between routes not found and other resource not found errors (since both have 404 status code)
            # TODO: Must standardize API response from server side
            if response_json.get('error_code', '') == "NOT_FOUND":
                raise ApiError(ExceptionResponse(success=False, detail="Not Found", error_code="NOT_FOUND"))
            
        try:
            # Check if response is an API error (TODO: Must standardize API response from server side)
            response = ExceptionResponse.model_validate(response_json)
            if raise_error:
                raise ApiError(response) 
        except pydantic.ValidationError:
            response = response_json
    

        return response
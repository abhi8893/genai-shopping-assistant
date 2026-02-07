from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


# TODO: UP046 Generic class `SuccessResponse` uses `Generic` subclass
# instead of type parameters
class SuccessResponse(BaseModel, Generic[T]):  # noqa: UP046
    success: bool = True
    message: str = "OK"
    data: T | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str | None = None
    errors: list[str] | None = None

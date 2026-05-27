from fastapi import status


# TODO: N818 Exception name `BaseAppException` should be named with an Error suffix
class BaseAppException(Exception):  # noqa: N818
    def __init__(
        self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return self.message


class ResourceNotFoundException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UnauthorizedException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ValidationException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class ForbiddenException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

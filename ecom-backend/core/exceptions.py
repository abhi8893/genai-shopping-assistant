from fastapi import status


class BaseAppException(Exception):
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

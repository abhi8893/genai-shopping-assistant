from pydantic import BaseModel


class ExceptionResponse(BaseModel):
    success: bool = False
    detail: str
    error_code: str

    class Config:
        from_attributes = True


class ApiError(Exception):
    def __init__(self, response: ExceptionResponse, message_context: str = None):
        super().__init__(self._construct_message(response, message_context))
        self.response = response

    @staticmethod
    def _construct_message(
        response: ExceptionResponse, message_context: str = None
    ) -> str:
        message = "\nResponse:\n"
        message += response.model_dump_json(indent=4)
        if message_context:
            message += f"\nContext:\n{message_context}"

        return message

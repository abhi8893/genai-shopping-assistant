from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.exceptions import BaseAppException

def app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": str(exc),
            "error_code": "APPLICATION_ERROR"
        }
    )


def register_exception_handlers(app: FastAPI):
    app.exception_handler(Exception)(app_exception_handler)
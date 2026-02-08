from core.exceptions import BaseAppException
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

# NOTE: Ref: https://medium.com/delivus/exception-handling-best-practices-in-python-a-fastapi-perspective-98ede2256870


# TODO: ARG001 Unused function argument: `request`
def app_exception_handler(request: Request, exc: BaseAppException):  # noqa: ARG001
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": str(exc),
            "error_code": "APPLICATION_ERROR",
        },
    )


# TODO: ARG001 Unused function argument: `request`
def uncaught_exception_handler(request: Request, exc: Exception):  # noqa: ARG001
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "detail": str(exc),
            "error_code": "UNCAUGHT_EXCEPTION",
        },
    )


def register_exception_handlers(app: FastAPI):
    app.exception_handler(Exception)(uncaught_exception_handler)
    app.exception_handler(BaseAppException)(app_exception_handler)

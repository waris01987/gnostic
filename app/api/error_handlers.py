from starlette import status
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from app.api.response import APIResponse
from app.common.errors import AppError


def setup_error_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return APIResponse.error(
            message=exc.message, status_code=exc.status_code, details=exc.details
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = []
        for err in exc.errors():
            error = {
                "location": err.get("loc", []),
                "message": err.get("msg"),
                "type": err.get("type"),
            }
            errors.append(error)

        return APIResponse.error(
            message="Validation Error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors},
        )

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class CustomExceptionHandlers:
    """Centralized exception handlers for consistent API error responses."""

    @staticmethod
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger = logging.getLogger("fibonacci_api")
        logger.warning(
            "http_exception path=%s status=%s detail=%s",
            request.url.path,
            exc.status_code,
            exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "message": exc.detail,
                    "path": request.url.path,
                }
            },
        )

    @staticmethod
    async def handle_validation_exception(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger = logging.getLogger("fibonacci_api")
        logger.warning("validation_error path=%s", request.url.path)
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "validation_error",
                    "message": "Request validation failed",
                    "path": request.url.path,
                    "details": exc.errors(),
                }
            },
        )

    @staticmethod
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        logger = logging.getLogger("fibonacci_api")
        logger.exception("unexpected_error path=%s", request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "path": request.url.path,
                }
            },
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all custom exception handlers to the FastAPI app."""
    app.add_exception_handler(StarletteHTTPException, CustomExceptionHandlers.handle_http_exception)
    app.add_exception_handler(RequestValidationError, CustomExceptionHandlers.handle_validation_exception)
    app.add_exception_handler(Exception, CustomExceptionHandlers.handle_unexpected_exception)
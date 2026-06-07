from __future__ import annotations

import logging
import time
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class LoggingHelper:
    """Encapsulates logging setup and request logging middleware."""

    LOGGER_NAME = "fibonacci_api"

    @staticmethod
    def configure_logging() -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        return logging.getLogger(LoggingHelper.LOGGER_NAME)

    @staticmethod
    async def log_requests(request: Request, call_next: Callable) -> JSONResponse:
        logger = logging.getLogger(LoggingHelper.LOGGER_NAME)
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


def register_request_logging(app: FastAPI) -> None:
    """Configure logging and attach request logging middleware to the app."""
    LoggingHelper.configure_logging()
    app.middleware("http")(LoggingHelper.log_requests)
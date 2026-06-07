from __future__ import annotations

from fastapi import FastAPI

from src.app.constants import APP_DESCRIPTION, APP_TITLE, APP_VERSION
from src.app.helper.exception_handlers import register_exception_handlers
from src.app.helper.logging_helper import register_request_logging
from src.app.router import router


def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_TITLE,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url=None,
    )

    register_exception_handlers(app)
    register_request_logging(app)
    app.include_router(router)
    return app


app = create_app()

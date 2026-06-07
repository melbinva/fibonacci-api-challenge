from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from src.app.constants import MAX_N
from src.app.fibonacci import fibonacci
from src.app.helper.landing_page import get_landing_page_html

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing_page() -> str:
    return get_landing_page_html()


@router.get("/swagger", include_in_schema=False)
def swagger_ui_alias() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@router.get("/fibonacci")
def get_fibonacci(n: Annotated[int, Query(description="Zero-based Fibonacci index")]) -> dict[str, int]:
    if n < 0:
        raise HTTPException(status_code=400, detail="n must be greater than or equal to 0")

    if n > MAX_N:
        raise HTTPException(
            status_code=400,
            detail=f"n is too large for this service. Maximum allowed value is {MAX_N}.",
        )

    return {"n": n, "value": fibonacci(n)}



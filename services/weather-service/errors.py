import logging
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

PROBLEM_MEDIA_TYPE = "application/problem+json"
RETRY_AFTER_SECONDS = 5

# The spec has no code for 405 or 500. 405 follows registry-service; 500 needs its own code.
FRAMEWORK_CODES = {404: "NOT_FOUND", 405: "VALIDATION"}


class UnavailableProblem(Exception):
    """FR-2.7: the provider failed and there is no forecast we may serve."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


def problem_response(
    status: int, code: str, detail: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    return JSONResponse(
        {
            "type": "about:blank",
            "title": HTTPStatus(status).phrase,
            "status": status,
            "detail": detail,
            "code": code,
        },
        status_code=status,
        headers=headers,
        media_type=PROBLEM_MEDIA_TYPE,
    )


def _describe(error: dict[str, Any]) -> str:
    source, *path = error["loc"]
    label = ".".join(part for part in path if isinstance(part, str)) or source
    return f"{label}: {error['msg']}"


async def _handle_unavailable(request: Request, exc: UnavailableProblem) -> JSONResponse:
    return problem_response(
        503, "UNAVAILABLE", exc.detail, {"Retry-After": str(RETRY_AFTER_SECONDS)}
    )


async def _handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    default = "INTERNAL" if exc.status_code >= 500 else "VALIDATION"
    code = FRAMEWORK_CODES.get(exc.status_code, default)
    return problem_response(exc.status_code, code, str(exc.detail), exc.headers)


async def _handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    detail = "; ".join(_describe(error) for error in exc.errors())
    return problem_response(422, "VALIDATION", detail)


async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unexpected error on %s %s", request.method, request.url.path, exc_info=exc)
    return problem_response(500, "INTERNAL", "Internal server error")


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UnavailableProblem, _handle_unavailable)
    app.add_exception_handler(StarletteHTTPException, _handle_http_error)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(Exception, _handle_unexpected)

import logging
from http import HTTPStatus
from typing import Any, ClassVar

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

PROBLEM_MEDIA_TYPE = "application/problem+json"
RETRY_AFTER_SECONDS = 5

# The spec has no code for 405 or 500; they follow registry-service (405) and need a new code (500).
FRAMEWORK_CODES = {404: "NOT_FOUND", 405: "VALIDATION"}


class ApiProblem(Exception):
    status: ClassVar[int]
    code: ClassVar[str]

    def __init__(self, detail: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        self.headers = headers


class ValidationProblem(ApiProblem):
    status = 422
    code = "VALIDATION"


class NotFoundProblem(ApiProblem):
    status = 404
    code = "NOT_FOUND"


class UpstreamUnavailable(ApiProblem):
    status = 503
    code = "UPSTREAM_UNAVAILABLE"

    def __init__(self, service: str, reason: str) -> None:
        super().__init__(
            f"{service} {reason}", headers={"Retry-After": str(RETRY_AFTER_SECONDS)}
        )


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


async def _handle_problem(request: Request, exc: ApiProblem) -> JSONResponse:
    return problem_response(exc.status, exc.code, exc.detail, exc.headers)


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
    app.add_exception_handler(ApiProblem, _handle_problem)
    app.add_exception_handler(StarletteHTTPException, _handle_http_error)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(Exception, _handle_unexpected)

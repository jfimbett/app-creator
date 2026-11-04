"""One error shape for every failure: {"error": {"code", "message", "details", "reference"}}.

- `AppError`: an expected failure raised by our own code (bad CIK, unknown company...).
- Request validation errors become 422 with a code chosen from the failing parameter.
- HTTP errors from routing (unknown path, wrong method) keep their status in the envelope.
- Anything unexpected becomes 500 `internal_error` with a generic message and a `reference` id;
  the detail goes only to the server log, never into the response.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.clients.sec import (
    SecContactNotConfigured,
    SecError,
    SecNotFound,
    SecRateLimited,
    SecRefused,
    UpstreamNotAllowed,
)

logger = logging.getLogger("sec_analytics.errors")

# Which error code a validation failure gets, by the name of the failing parameter.
_CODE_BY_PARAM = {
    "q": "invalid_query",
    "limit": "invalid_query",
    "cik": "invalid_cik",
    "years": "invalid_years",
}
_MESSAGE_BY_CODE = {
    "invalid_query": "Search needs 1 to 100 characters and a limit from 1 to 20.",
    "invalid_cik": "A CIK has up to 10 digits",
    "invalid_request": "The request has an invalid parameter.",
    "invalid_years": "Choose from 5 to 10 years.",
}
_HTTP_CODES = {404: "not_found", 405: "method_not_allowed"}


class AppError(Exception):
    """An expected failure with a stable `code`, a plain `message` and an HTTP `status`."""

    def __init__(
        self, code: str, message: str, status: int, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details


def error_response(
    status: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    reference: str | None = None,
) -> JSONResponse:
    """Build a JSON response in the error envelope."""
    body = {"code": code, "message": message, "details": details, "reference": reference}
    return JSONResponse(status_code=status, content={"error": body})


async def _app_error(_: Request, exc: AppError) -> JSONResponse:
    return error_response(exc.status, exc.code, exc.message, exc.details)


def _validation_code(exc: RequestValidationError, path: str) -> tuple[str, list[str]]:
    """Pick the error code from the first failing parameter; list the parameter names.

    The M1 overview accepts a wider `years` range and keeps its `invalid_request` code.
    """
    params = [str(err["loc"][-1]) for err in exc.errors() if err.get("loc")]
    own_years_range = path.endswith(("/overview", "/filings"))
    usable = [p for p in params if not (p == "years" and own_years_range)]
    code = next((_CODE_BY_PARAM[p] for p in usable if p in _CODE_BY_PARAM), "invalid_request")
    return code, params


async def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    code, params = _validation_code(exc, request.url.path)
    return error_response(422, code, _MESSAGE_BY_CODE[code], {"parameters": params})


async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = _HTTP_CODES.get(exc.status_code, "http_error")
    message = "No such API path." if exc.status_code == 404 else str(exc.detail)
    return error_response(exc.status_code, code, message)


NOT_CONFIGURED_MESSAGE = (
    "Live SEC data is not configured: set SEC_USER_AGENT (see .env.example and docs/SETUP.md)"
)


async def _sec_error(_: Request, exc: SecError) -> JSONResponse:
    """Map a client error to the API's codes. The configured contact is never in a message."""
    if isinstance(exc, SecContactNotConfigured):
        return error_response(503, exc.code, NOT_CONFIGURED_MESSAGE, {"setting": "SEC_USER_AGENT"})
    if isinstance(exc, SecRateLimited):
        wait = round(exc.retry_after)
        message = f"SEC is limiting requests; try again in {wait} s"
        return error_response(503, exc.code, message, {"retry_after": wait})
    if isinstance(exc, SecRefused):
        message = "SEC refused the request (403). The app does not retry refused requests."
        return error_response(502, exc.code, message)
    if isinstance(exc, UpstreamNotAllowed):
        message = "SEC pointed to an address outside the allowlist, so it was not requested."
        return error_response(502, exc.code, message)
    if isinstance(exc, SecNotFound):
        return error_response(404, "company_not_found", "SEC has no record for this CIK.")
    return error_response(502, "sec_unavailable", "SEC is unavailable right now")


async def _unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    reference = uuid.uuid4().hex[:12]
    logger.error(
        "Unexpected error %s on %s %s", reference, request.method, request.url.path, exc_info=exc
    )
    message = f"Something went wrong on the server. Reference: {reference}."
    return error_response(500, "internal_error", message, reference=reference)


def install_error_handlers(app: FastAPI) -> None:
    """Register the envelope handlers on `app`."""
    app.add_exception_handler(AppError, _app_error)
    app.add_exception_handler(SecError, _sec_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(Exception, _unexpected_error)

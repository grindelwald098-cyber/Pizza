import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import (
    AppError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalError,
    NotFoundError,
    UnauthorizedError,
)

logger = logging.getLogger(__name__)


def error_response(
    status_code: int,
    detail: object,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
        headers=headers,
    )


def _from_app_error(exc: AppError) -> JSONResponse:
    return error_response(exc.status_code, exc.detail, exc.headers)


async def bad_request_handler(
    _request: Request,
    exc: BadRequestError,
) -> JSONResponse:
    return _from_app_error(exc)


async def unauthorized_handler(
    _request: Request,
    exc: UnauthorizedError,
) -> JSONResponse:
    return _from_app_error(exc)


async def forbidden_handler(
    _request: Request,
    exc: ForbiddenError,
) -> JSONResponse:
    return _from_app_error(exc)


async def not_found_handler(
    _request: Request,
    exc: NotFoundError,
) -> JSONResponse:
    return _from_app_error(exc)


async def conflict_handler(
    _request: Request,
    exc: ConflictError,
) -> JSONResponse:
    return _from_app_error(exc)


async def internal_error_handler(
    request: Request,
    exc: InternalError,
) -> JSONResponse:
    logger.error(
        "Internal error on %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return _from_app_error(exc)


async def app_error_handler(
    _request: Request,
    exc: AppError,
) -> JSONResponse:
    return _from_app_error(exc)


async def validation_error_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return error_response(HTTPStatus.UNPROCESSABLE_ENTITY, exc.errors())


async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    headers = dict(exc.headers) if exc.headers else None
    return error_response(exc.status_code, exc.detail, headers)


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return error_response(
        HTTPStatus.INTERNAL_SERVER_ERROR,
        "Internal server error",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BadRequestError, bad_request_handler)
    app.add_exception_handler(UnauthorizedError, unauthorized_handler)
    app.add_exception_handler(ForbiddenError, forbidden_handler)
    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(ConflictError, conflict_handler)
    app.add_exception_handler(InternalError, internal_error_handler)
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

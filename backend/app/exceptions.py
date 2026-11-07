from http import HTTPStatus


class AppError(Exception):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    default_detail = "Internal server error"

    def __init__(
        self,
        detail: str | None = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.detail = self.default_detail if detail is None else detail
        self.headers = headers
        super().__init__(self.detail)


class BadRequestError(AppError):
    status_code = HTTPStatus.BAD_REQUEST
    default_detail = "Bad request"


class UnauthorizedError(AppError):
    status_code = HTTPStatus.UNAUTHORIZED
    default_detail = "Unauthorized"

    @classmethod
    def bearer(
        cls,
        detail: str = "Invalid or expired token",
    ) -> "UnauthorizedError":
        return cls(detail, headers={"WWW-Authenticate": "Bearer"})


class ForbiddenError(AppError):
    status_code = HTTPStatus.FORBIDDEN
    default_detail = "Forbidden"


class NotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND
    default_detail = "Not found"


class ConflictError(AppError):
    status_code = HTTPStatus.CONFLICT
    default_detail = "Conflict"


class InternalError(AppError):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    default_detail = "Internal server error"

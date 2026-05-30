from app.schemas.response import ErrorItem


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        errors: list[ErrorItem] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(
        self,
        message: str = "Resource not found",
        errors: list[ErrorItem] | None = None,
    ) -> None:
        super().__init__(message, status_code=404, errors=errors)


class ConflictError(AppException):
    def __init__(
        self,
        message: str = "Conflict",
        errors: list[ErrorItem] | None = None,
    ) -> None:
        super().__init__(message, status_code=409, errors=errors)


class ValidationAppError(AppException):
    """Business-rule validation (not Pydantic request validation)."""

    def __init__(
        self,
        message: str = "Validation failed",
        errors: list[ErrorItem] | None = None,
    ) -> None:
        super().__init__(message, status_code=422, errors=errors)


class UnauthorizedError(AppException):
    def __init__(
        self,
        message: str = "Unauthorized",
        errors: list[ErrorItem] | None = None,
    ) -> None:
        super().__init__(message, status_code=401, errors=errors)


class ForbiddenError(AppException):
    def __init__(
        self,
        message: str = "Forbidden",
        errors: list[ErrorItem] | None = None,
    ) -> None:
        super().__init__(message, status_code=403, errors=errors)

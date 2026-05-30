from typing import TypeVar

from app.core.exceptions import NotFoundError, ValidationAppError
from app.schemas.response import ErrorItem

T = TypeVar("T")


def ensure_found(value: T | None, message: str = "Resource not found") -> T:
    if value is None:
        raise NotFoundError(message)
    return value


def ensure_positive_id(value: int, field: str = "id") -> int:
    if value < 1:
        raise ValidationAppError(
            message="Invalid id",
            errors=[ErrorItem(field=field, message="Must be a positive integer")],
        )
    return value


def ensure_business_rules(errors: list[ErrorItem]) -> None:
    if errors:
        raise ValidationAppError(message="Validation failed", errors=errors)

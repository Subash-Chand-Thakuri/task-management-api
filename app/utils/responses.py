import math
from typing import TypeVar

from app.schemas.response import ApiResponse, ErrorItem, PaginatedData, PaginationMeta

T = TypeVar("T")


def success_response(
    data: T | None = None,
    message: str = "OK",
) -> ApiResponse[T]:
    return ApiResponse(success=True, message=message, data=data)


def error_response(
    message: str,
    errors: list[ErrorItem] | None = None,
) -> ApiResponse[None]:
    return ApiResponse(success=False, message=message, data=None, errors=errors or None)


def paginated_response(
    items: list[T],
    *,
    page: int,
    page_size: int,
    total: int,
    message: str = "OK",
) -> ApiResponse[PaginatedData[T]]:
    total_pages = math.ceil(total / page_size) if page_size else 0
    payload = PaginatedData(
        items=items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )
    return ApiResponse(success=True, message=message, data=payload)

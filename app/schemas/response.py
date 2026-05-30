from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorItem(BaseModel):
    field: str | None = None
    message: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None
    errors: list[ErrorItem] | None = None


class PaginationMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    pagination: PaginationMeta


PaginatedResponse = ApiResponse[PaginatedData[T]]

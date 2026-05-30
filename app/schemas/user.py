from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    is_active: bool = True
    role_id: int | None = None
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    name: str
    password: str
    role_id: int


class UserUpdate(BaseModel):
    email: str | None = Field(default=None, min_length=3, max_length=255)
    name: str | None = None
    password: str | None = None
    role_id: int | None = None
    is_active: bool | None = None

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.task import TaskStatus
from app.utils.datetime_utils import to_naive_utc


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    description: str | None
    status: TaskStatus
    due_date: datetime | None
    assigned_to: int | None
    created_by: int | None
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    assigned_to: int | None = None

    @field_validator("due_date", mode="after")
    @classmethod
    def normalize_due_date(cls, value: datetime | None) -> datetime | None:
        return to_naive_utc(value)


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_date: datetime | None = None
    assigned_to: int | None = None

    @field_validator("due_date", mode="after")
    @classmethod
    def normalize_due_date(cls, value: datetime | None) -> datetime | None:
        return to_naive_utc(value)

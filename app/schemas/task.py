from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.task import TaskStatus


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
    created_by: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_date: datetime | None = None
    assigned_to: int | None = None

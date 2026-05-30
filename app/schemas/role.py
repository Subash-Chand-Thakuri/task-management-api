from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.role import RoleNameEnum


class Role(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: RoleNameEnum
    created_at: datetime
    updated_at: datetime


class RoleCreate(BaseModel):
    name: RoleNameEnum


class RoleUpdate(BaseModel):
    name: RoleNameEnum | None = None

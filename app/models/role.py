from sqlalchemy import Column, Integer, String, DateTime, func, Enum

from app.db.base import Base

class RoleNameEnum(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(RoleNameEnum), index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
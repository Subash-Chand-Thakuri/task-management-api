from typing import Literal

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationAppError
from app.models.task import Task as TaskModel, TaskStatus
from app.schemas.response import ErrorItem
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.utils.validators import ensure_business_rules, ensure_found

from app.models.role import RoleNameEnum
from app.api.deps import AuthContext
_NOT_FOUND = "Task not found"
_SORTABLE_FIELDS = frozenset({"id", "title", "status", "due_date", "created_at", "updated_at"})


def _apply_task_role_filter(query, auth: AuthContext):
    if auth.role == RoleNameEnum.ADMIN:
        return query
    if auth.role == RoleNameEnum.MANAGER:
        return query.where(
            or_(
                TaskModel.assigned_to == auth.user.id,
                TaskModel.created_by == auth.user.id,
            )
        )
    return query.where(TaskModel.assigned_to == auth.user.id)


async def _get_accessible_task(
    session: AsyncSession, task_id: int, auth: AuthContext
) -> TaskModel:
    query = _apply_task_role_filter(
        select(TaskModel).where(TaskModel.id == task_id), auth
    )
    result = await session.execute(query)
    return ensure_found(result.scalar_one_or_none(), _NOT_FOUND)


async def list_tasks(
    session: AsyncSession,
    auth: AuthContext,
    *,
    page: int = 1,
    page_size: int = 10,
    sort: str = "created_at",
    order: Literal["asc", "desc"] = "asc",
    search: str | None = None,
) -> tuple[list[Task], int]:
    query = _apply_task_role_filter(select(TaskModel), auth)
    
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                TaskModel.title.ilike(pattern),
                TaskModel.description.ilike(pattern),
            )
        )

    if sort not in _SORTABLE_FIELDS:
        raise ValidationAppError(f"Invalid sort field: {sort}")

    sort_column = getattr(TaskModel, sort)
    order_clause = asc(sort_column) if order == "asc" else desc(sort_column)

    total = (
        await session.execute(select(func.count()).select_from(query.subquery()))
    ).scalar_one()

    result = await session.execute(
        query.order_by(order_clause)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    tasks = [Task.model_validate(task) for task in result.scalars().all()]
    return tasks, total


async def get_task(session: AsyncSession, task_id: int, auth: AuthContext) -> Task:
    task = await _get_accessible_task(session, task_id, auth)
    return Task.model_validate(task)


async def create_task(
    session: AsyncSession, data: TaskCreate, *, created_by: int
) -> Task:
    task = TaskModel(
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        assigned_to=data.assigned_to,
        created_by=created_by,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return Task.model_validate(task)


async def update_task(
    session: AsyncSession, task_id: int, data: TaskUpdate, auth: AuthContext
) -> Task:
    task = await _get_accessible_task(session, task_id, auth)

    updates = data.model_dump(exclude_unset=True)
    if auth.role != RoleNameEnum.ADMIN:
        updates = {
            k: v for k, v in updates.items() if k in ("status")
        }

    if "status" in updates:
        if (
            task.status == TaskStatus.COMPLETED
            and updates["status"] == TaskStatus.PENDING
        ):
            ensure_business_rules(
                [
                    ErrorItem(
                        field="status",
                        message="Completed tasks cannot be reverted to pending",
                    )
                ]
            )

    for field, value in updates.items():
        setattr(task, field, value)

    await session.commit()
    await session.refresh(task)
    return Task.model_validate(task)


async def delete_task(session: AsyncSession, task_id: int) -> None:
    task = await session.get(TaskModel, task_id)
    ensure_found(task, _NOT_FOUND)
    await session.delete(task)
    await session.commit()

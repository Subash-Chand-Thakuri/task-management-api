from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.task import Task as TaskModel
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.utils.validators import ensure_found

_NOT_FOUND = "Task not found"


async def list_tasks(session: AsyncSession) -> list[Task]:
    result = await session.execute(select(TaskModel).order_by(TaskModel.id))
    return [Task.model_validate(task) for task in result.scalars().all()]


async def get_task(session: AsyncSession, task_id: int) -> Task:
    task = await session.get(TaskModel, task_id)
    ensure_found(task, _NOT_FOUND)
    return Task.model_validate(task)


async def create_task(session: AsyncSession, data: TaskCreate) -> Task:
    task = TaskModel(
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        assigned_to=data.assigned_to,
        created_by=data.created_by,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return Task.model_validate(task)


async def update_task(session: AsyncSession, task_id: int, data: TaskUpdate) -> Task:
    task = await session.get(TaskModel, task_id)
    ensure_found(task, _NOT_FOUND)

    updates = data.model_dump(exclude_unset=True)
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

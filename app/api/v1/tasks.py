from fastapi import APIRouter, Depends, status

from app.api.deps import DbSession, RequireAnyRole, require_any_role
from app.schemas.response import ApiResponse
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.services import task_service
from app.utils.responses import success_response
from app.utils.validators import ensure_positive_id

# JWT + role check on every task route (like router.use(auth) in Express)
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(require_any_role)],
)


@router.get("/", response_model=ApiResponse[list[Task]])
async def list_tasks(session: DbSession, auth: RequireAnyRole):
    tasks = await task_service.list_tasks(session)
    return success_response(tasks)


@router.post("/", response_model=ApiResponse[Task], status_code=status.HTTP_201_CREATED)
async def create_task(session: DbSession, data: TaskCreate, auth: RequireAnyRole):
    task = await task_service.create_task(session, data)
    return success_response(task, message="Task created")


@router.get("/{task_id}", response_model=ApiResponse[Task])
async def get_task(session: DbSession, task_id: int, auth: RequireAnyRole):
    ensure_positive_id(task_id, field="task_id")
    task = await task_service.get_task(session, task_id)
    return success_response(task)


@router.put("/{task_id}", response_model=ApiResponse[Task])
async def update_task(
    session: DbSession,
    task_id: int,
    data: TaskUpdate,
    auth: RequireAnyRole,
):
    ensure_positive_id(task_id, field="task_id")
    task = await task_service.update_task(session, task_id, data)
    return success_response(task, message="Task updated")


@router.delete("/{task_id}", response_model=ApiResponse[None])
async def delete_task(session: DbSession, task_id: int, auth: RequireAnyRole):
    ensure_positive_id(task_id, field="task_id")
    await task_service.delete_task(session, task_id)
    return success_response(message="Task deleted")

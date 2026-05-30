from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import DbSession, RequireAdmin, RequireAnyRole, require_any_role, RequireManagerOrAdmin
from app.schemas.response import ApiResponse, PaginatedData
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.services import task_service
from app.utils.responses import paginated_response, success_response
from app.utils.validators import ensure_positive_id

# JWT + role check on every task route (like router.use(auth) in Express)
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(require_any_role)],
)


@router.get("/", response_model=ApiResponse[PaginatedData[Task]])
async def list_tasks(
    session: DbSession,
    auth: RequireAnyRole,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    sort: str = Query("created_at"),
    order: Literal["asc", "desc"] = Query("asc"),
    search: str | None = Query(None),
):
    tasks, total = await task_service.list_tasks(
        session,
        auth,
        page=page,
        page_size=page_size,
        sort=sort,
        order=order,
        search=search,
    )
    return paginated_response(tasks, page=page, page_size=page_size, total=total)


@router.post("/", response_model=ApiResponse[Task], status_code=status.HTTP_201_CREATED)
async def create_task(session: DbSession, data: TaskCreate, auth: RequireManagerOrAdmin):
    task = await task_service.create_task(session, data, created_by=auth.user.id)
    return success_response(task, message="Task created")


@router.get("/{task_id}", response_model=ApiResponse[Task])
async def get_task(session: DbSession, task_id: int, auth: RequireAnyRole):
    ensure_positive_id(task_id, field="task_id")
    task = await task_service.get_task(session, task_id, auth)
    return success_response(task)


@router.put("/{task_id}", response_model=ApiResponse[Task])
async def update_task(
    session: DbSession,
    task_id: int,
    data: TaskUpdate,
    auth: RequireAnyRole,
):
    ensure_positive_id(task_id, field="task_id")
    task = await task_service.update_task(session, task_id, data, auth)
    return success_response(task, message="Task updated")


@router.delete("/{task_id}", response_model=ApiResponse[None])
async def delete_task(session: DbSession, task_id: int, auth: RequireAdmin):
    ensure_positive_id(task_id, field="task_id")
    await task_service.delete_task(session, task_id)
    return success_response(message="Task deleted")

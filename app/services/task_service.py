from app.models.task import Task

def get_dummy_tasks() -> list[Task]:
    return [
        Task(id=1, title="Task 1", description="Description 1", status="pending", assigned_to=1, created_by=1),
        Task(id=2, title="Task 2", description="Description 2", status="in_progress", assigned_to=2, created_by=2),
    ]
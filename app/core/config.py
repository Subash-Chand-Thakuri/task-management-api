from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Task Management System RBAC API "
    debug: bool = True
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5435/task_management_db"
    )

    class Config:
        env_file = ".env"


settings = Settings()

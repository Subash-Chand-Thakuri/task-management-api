from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # only app required settings from env file
    app_name: str = "Task Management System RBAC API"
    debug: bool = True
    database_url: str
    jwt_secret_key: str = "jwt_secret_key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    admin_email: str = "admin@mailsac.com"
    admin_password: str = "Password111!"
    admin_name: str = "System Admin"
    seed_on_startup: bool = True

    @property
    def database_url_sync(self) -> str:
        return self.database_url.replace("+asyncpg", "+psycopg2")


settings = Settings()

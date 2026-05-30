import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging_config import configure_app_logging
from app.db.seed import run_seed

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_app_logging()
    if settings.seed_on_startup:
        logger.info("Running database seed...")
        await run_seed()
    yield


app = FastAPI(title="task-management-api", lifespan=lifespan)
register_exception_handlers(app)
app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

from fastapi import FastAPI

from app.api import api_router


app = FastAPI(title="task-management-api")
app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

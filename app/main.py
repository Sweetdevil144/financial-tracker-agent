from contextlib import asynccontextmanager

from fastapi import FastAPI
from uvicorn import run
from app.api.routes.analytics import
from app.database.db import Database
from app.api.routes.v1_router import v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    _db = await Database.connect()
    yield
    await Database.disconnect()


def create_app():
    app = FastAPI(
        title="Langchain Agent",
        docs_url="/docs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    @app.get("/")
    async def root():
        return {"message": "Financial Tracker Agent"}

    app.include_router(v1_router)
    return app


app = create_app()

if __name__ == "__main__":
    run(app="app.main:app", host="0.0.0.0", port=8000, reload=True)

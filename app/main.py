from contextlib import asynccontextmanager

from fastapi import FastAPI
from uvicorn import run

from app.database.db import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: initialize and teardown for app."""
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
        return {"message": "Hello World"}

    return app


app = create_app()

if __name__ == "__main__":
    run(app="app.main:app", host="0.0.0.0", port=8000, reload=True)

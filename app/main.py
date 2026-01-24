from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from app.api.routes.v1_router import v1_router
from app.database.db import Database
from app.config import config


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

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {"message": "Financial Tracker Agent"}

    app.include_router(v1_router)
    return app


app = create_app()

if __name__ == "__main__":
    run(app="app.main:app", host="0.0.0.0", port=int(config.PORT), reload=True)

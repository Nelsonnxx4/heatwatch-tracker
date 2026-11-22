from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401
from app.config import get_settings
from app.db import Base, engine, ensure_schema
from app.routers import cities, rankings


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await ensure_schema(conn)
    yield
    await engine.dispose()


app = FastAPI(
    title="HeatWatch Global API",
    description="Hourly heat, humidity, and wind data for major world cities.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_methods=["GET"],
    allow_headers=["X-API-Key"],
)

app.include_router(cities.router)
app.include_router(rankings.router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}

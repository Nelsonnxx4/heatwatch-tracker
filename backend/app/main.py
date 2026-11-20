from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.config import get_settings
from app.db import Base, engine
from app.routers import cities, rankings


@asynccontextmanager
async def lifespan(_: FastAPI):
    # MVP convenience. Swap for Alembic migrations before the schema starts changing.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="HeatWatch Nigeria API",
    description="Hourly temperature and heat-index data for Nigerian cities.",
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

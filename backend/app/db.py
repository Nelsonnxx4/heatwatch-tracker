from collections.abc import AsyncIterator

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


def _add_missing_observation_columns(connection: Connection) -> None:
    inspector = inspect(connection)
    if "observations" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("observations")}
    additions = {
        "wind_speed_kmh": "FLOAT",
        "wind_direction_deg": "FLOAT",
    }
    for name, column_type in additions.items():
        if name not in existing:
            connection.execute(
                text(f"ALTER TABLE observations ADD COLUMN {name} {column_type}")
            )


def _add_missing_city_columns(connection: Connection) -> None:
    inspector = inspect(connection)
    if "cities" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("cities")}
    if "country" not in existing:
        connection.execute(
            text("ALTER TABLE cities ADD COLUMN country VARCHAR(64) DEFAULT 'Nigeria'")
        )
    connection.execute(text("UPDATE cities SET country = 'Nigeria' WHERE country IS NULL"))


async def ensure_schema(connection: AsyncConnection) -> None:
    await connection.run_sync(_add_missing_observation_columns)
    await connection.run_sync(_add_missing_city_columns)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session

import os

# Must be set before the app is imported so settings pick them up.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["API_KEYS"] = "test-key"

from datetime import datetime, timedelta  # noqa: E402

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db import Base, get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models import City, Observation  # noqa: E402

BASE_TIME = datetime(2026, 11, 18, 0, 0)  # naive UTC, 72 hourly rows -> 3 days


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session_factory):
    async def override_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers={"X-API-Key": "test-key"}
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def anon_client(session_factory):
    async def override_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seeded(session_factory):
    """Makurdi is hot and humid, Lagos is milder, so Makurdi must rank first."""
    async with session_factory() as session:
        makurdi = City(slug="makurdi", name="Makurdi", state="Benue", latitude=7.7337, longitude=8.5214)
        lagos = City(slug="lagos", name="Lagos", state="Lagos", latitude=6.5244, longitude=3.3792)
        session.add_all([makurdi, lagos])
        await session.flush()
        for hour in range(72):
            stamp = BASE_TIME + timedelta(hours=hour)
            session.add(Observation(city_id=makurdi.id, observed_at=stamp, temperature_c=36.0, humidity_pct=55.0))
            session.add(Observation(city_id=lagos.id, observed_at=stamp, temperature_c=28.0, humidity_pct=60.0))
        await session.commit()

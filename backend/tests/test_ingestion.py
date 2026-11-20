from datetime import datetime

from sqlalchemy import func, select

from app.ingestion.open_meteo import parse_hourly
from app.ingestion.store import store_observations
from app.models import City, Observation
from app.seed import CITIES, seed_cities

PAYLOAD = {
    "hourly": {
        "time": ["2026-11-20T10:00", "2026-11-20T11:00", "2026-11-20T12:00", "2026-11-20T13:00"],
        "temperature_2m": [31.2, None, 33.5, 35.0],
        "relative_humidity_2m": [55, 54, None, 50],
    }
}


def test_parse_skips_missing_temperature():
    rows = parse_hourly(PAYLOAD)
    assert [r["observed_at"].hour for r in rows] == [10, 12, 13]


def test_parse_keeps_missing_humidity_as_none():
    rows = parse_hourly(PAYLOAD)
    assert rows[1]["humidity_pct"] is None


def test_parse_drops_future_hours():
    rows = parse_hourly(PAYLOAD, until=datetime(2026, 11, 20, 12, 0))
    assert [r["observed_at"].hour for r in rows] == [10, 12]


def test_parse_handles_empty_payload():
    assert parse_hourly({}) == []


async def test_store_is_idempotent(session_factory):
    async with session_factory() as session:
        city = City(slug="abuja", name="Abuja", state="FCT", latitude=9.0, longitude=7.4)
        session.add(city)
        await session.commit()

        rows = parse_hourly(PAYLOAD)
        assert await store_observations(session, city.id, rows) == 3
        assert await store_observations(session, city.id, rows) == 0
        count = await session.scalar(select(func.count()).select_from(Observation))
        assert count == 3


async def test_seed_is_idempotent(session_factory):
    async with session_factory() as session:
        assert await seed_cities(session) == len(CITIES)
        assert await seed_cities(session) == 0

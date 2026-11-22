import asyncio
import logging
from datetime import UTC, datetime

import httpx
from sqlalchemy import select

from app import models  # noqa: F401
from app.db import Base, SessionLocal, engine, ensure_schema
from app.ingestion.open_meteo import fetch_hourly, parse_hourly
from app.ingestion.store import store_observations
from app.models import City
from app.seed import seed_cities

logger = logging.getLogger("ingestion")
FETCH_CONCURRENCY = 6


async def fetch_city_weather(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    city: tuple[int, str, float, float],
) -> tuple[tuple[int, str, float, float], dict | None]:
    _, slug, latitude, longitude = city
    try:
        async with semaphore:
            payload = await fetch_hourly(client, latitude, longitude)
        return city, payload
    except Exception:
        logger.exception("Weather fetch failed for %s", slug)
        return city, None


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await ensure_schema(conn)

    async with SessionLocal() as session:
        await seed_cities(session)
        cities = [
            (city.id, city.slug, city.latitude, city.longitude)
            for city in (await session.scalars(select(City))).all()
        ]

        semaphore = asyncio.Semaphore(FETCH_CONCURRENCY)
        async with httpx.AsyncClient(timeout=20) as client:
            results = await asyncio.gather(
                *(fetch_city_weather(client, semaphore, city) for city in cities)
            )

            for (city_id, slug, _, _), payload in results:
                if payload is None:
                    continue
                try:
                    now = datetime.now(UTC).replace(tzinfo=None)
                    rows = parse_hourly(payload, until=now)
                    added = await store_observations(session, city_id, rows)
                    logger.info("%s: %s new rows", slug, added)
                except Exception:
                    logger.exception("Ingestion failed for %s", slug)
                    await session.rollback()

    await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    asyncio.run(main())

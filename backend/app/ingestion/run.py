"""Ingestion job: python -m app.ingestion.run

Pulls recent hourly data for every city and stores new rows. Run it on a schedule
(cron, EventBridge + Lambda/ECS, GitHub Actions) every hour or so.
"""
import asyncio
import logging
from datetime import UTC, datetime

import httpx
from sqlalchemy import select

from app import models  # noqa: F401
from app.db import Base, SessionLocal, engine
from app.ingestion.open_meteo import fetch_hourly, parse_hourly
from app.ingestion.store import store_observations
from app.models import City
from app.seed import seed_cities

logger = logging.getLogger("ingestion")


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        await seed_cities(session)
        cities = (await session.scalars(select(City))).all()

        async with httpx.AsyncClient(timeout=20) as client:
            for city in cities:
                try:
                    payload = await fetch_hourly(client, city.latitude, city.longitude)
                    now = datetime.now(UTC).replace(tzinfo=None)
                    rows = parse_hourly(payload, until=now)
                    added = await store_observations(session, city.id, rows)
                    logger.info("%s: %s new rows", city.slug, added)
                except Exception:
                    logger.exception("Ingestion failed for %s", city.slug)
                    await session.rollback()

    await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    asyncio.run(main())

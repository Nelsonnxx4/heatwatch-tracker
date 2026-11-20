from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Observation


async def store_observations(session: AsyncSession, city_id: int, rows: list[dict]) -> int:
    """Insert rows that are not stored yet. Returns how many were new (idempotent)."""
    if not rows:
        return 0
    times = [r["observed_at"] for r in rows]
    existing = set(
        (
            await session.scalars(
                select(Observation.observed_at).where(
                    Observation.city_id == city_id, Observation.observed_at.in_(times)
                )
            )
        ).all()
    )
    new = [Observation(city_id=city_id, **r) for r in rows if r["observed_at"] not in existing]
    session.add_all(new)
    await session.commit()
    return len(new)

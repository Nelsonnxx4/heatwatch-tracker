from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Observation


async def store_observations(session: AsyncSession, city_id: int, rows: list[dict]) -> int:
    if not rows:
        return 0
    times = [r["observed_at"] for r in rows]
    existing = {
        observation.observed_at: observation
        for observation in (
            await session.scalars(
                select(Observation).where(
                    Observation.city_id == city_id,
                    Observation.observed_at.in_(times),
                )
            )
        ).all()
    }
    new = []
    for row in rows:
        observation = existing.get(row["observed_at"])
        if observation is None:
            new.append(Observation(city_id=city_id, **row))
            continue
        observation.temperature_c = row["temperature_c"]
        observation.humidity_pct = row.get("humidity_pct")
        observation.wind_speed_kmh = row.get("wind_speed_kmh")
        observation.wind_direction_deg = row.get("wind_direction_deg")

    session.add_all(new)
    await session.commit()
    return len(new)

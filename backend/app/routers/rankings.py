from datetime import timedelta

import pandas as pd
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import require_api_key
from app.models import City, Observation
from app.schemas import CityOut, RankingItem
from app.services.heat import heat_category, heat_index_series

router = APIRouter(prefix="/rankings", tags=["rankings"], dependencies=[Depends(require_api_key)])


@router.get("/hottest", response_model=list[RankingItem])
async def hottest(
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=10, ge=1, le=50),
    session: AsyncSession = Depends(get_session),
):
    """Cities ranked by peak heat index over the last `hours` of stored data."""
    latest = await session.scalar(select(func.max(Observation.observed_at)))
    if latest is None:
        return []

    since = latest - timedelta(hours=hours)
    result = await session.execute(
        select(Observation, City)
        .join(City, Observation.city_id == City.id)
        .where(Observation.observed_at >= since)
    )
    pairs = result.all()
    cities = {city.id: city for _, city in pairs}

    frame = pd.DataFrame(
        [(o.city_id, o.temperature_c, o.humidity_pct) for o, _ in pairs],
        columns=["city_id", "temperature_c", "humidity_pct"],
    )
    frame["heat_index_c"] = heat_index_series(frame["temperature_c"], frame["humidity_pct"])
    peak = frame.groupby("city_id")["heat_index_c"].max().sort_values(ascending=False).head(limit)

    return [
        RankingItem(
            city=CityOut.model_validate(cities[int(city_id)]),
            heat_index_max_c=float(value),
            heat_category=heat_category(float(value)),
        )
        for city_id, value in peak.items()
    ]

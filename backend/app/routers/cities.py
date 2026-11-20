from datetime import datetime, timedelta

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import require_api_key
from app.models import City, Observation
from app.schemas import CityOut, DailyOut, HeatSummaryOut, ObservationOut
from app.services.heat import (
    build_daily_summary,
    compute_anomaly,
    heat_category,
    heat_index_c,
)
from app.utils import to_naive_utc

router = APIRouter(prefix="/cities", tags=["cities"], dependencies=[Depends(require_api_key)])


async def _get_city_or_404(session: AsyncSession, slug: str) -> City:
    city = await session.scalar(select(City).where(City.slug == slug))
    if city is None:
        raise HTTPException(status_code=404, detail=f"City '{slug}' not found")
    return city


def to_observation_out(obs: Observation) -> ObservationOut:
    hi = heat_index_c(obs.temperature_c, obs.humidity_pct)
    return ObservationOut(
        observed_at=obs.observed_at,
        temperature_c=obs.temperature_c,
        humidity_pct=obs.humidity_pct,
        heat_index_c=hi,
        heat_category=heat_category(hi),
    )


@router.get("", response_model=list[CityOut])
async def list_cities(session: AsyncSession = Depends(get_session)):
    result = await session.scalars(select(City).order_by(City.name))
    return result.all()


@router.get("/{slug}/temperature", response_model=list[ObservationOut])
async def city_temperature(
    slug: str,
    start: datetime | None = Query(default=None, alias="from"),
    end: datetime | None = Query(default=None, alias="to"),
    limit: int = Query(default=168, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
):
    """Hourly readings, oldest first. Without `from`/`to`, returns the latest `limit` hours."""
    city = await _get_city_or_404(session, slug)
    if start is not None and end is not None and start > end:
        raise HTTPException(status_code=422, detail="'from' must not be after 'to'")

    stmt = select(Observation).where(Observation.city_id == city.id)
    if start is not None:
        stmt = stmt.where(Observation.observed_at >= to_naive_utc(start))
    if end is not None:
        stmt = stmt.where(Observation.observed_at <= to_naive_utc(end))
    stmt = stmt.order_by(Observation.observed_at.desc()).limit(limit)

    rows = (await session.scalars(stmt)).all()
    return [to_observation_out(o) for o in reversed(rows)]


@router.get("/{slug}/heat-summary", response_model=HeatSummaryOut)
async def heat_summary(
    slug: str,
    days: int = Query(default=7, ge=1, le=30),
    session: AsyncSession = Depends(get_session),
):
    city = await _get_city_or_404(session, slug)
    latest = await session.scalar(
        select(func.max(Observation.observed_at)).where(Observation.city_id == city.id)
    )
    if latest is None:
        raise HTTPException(status_code=404, detail="No observations yet for this city")

    since = latest - timedelta(days=days)
    rows = (
        await session.scalars(
            select(Observation)
            .where(Observation.city_id == city.id, Observation.observed_at >= since)
            .order_by(Observation.observed_at)
        )
    ).all()

    frame = pd.DataFrame(
        [
            {
                "observed_at": o.observed_at,
                "temperature_c": o.temperature_c,
                "humidity_pct": o.humidity_pct,
            }
            for o in rows
        ]
    )
    daily = build_daily_summary(frame)

    return HeatSummaryOut(
        city=CityOut.model_validate(city),
        current=to_observation_out(rows[-1]),
        days=[
            DailyOut(
                day=r.date,
                temp_min_c=r.temp_min_c,
                temp_max_c=r.temp_max_c,
                temp_mean_c=r.temp_mean_c,
                heat_index_max_c=r.heat_index_max_c,
            )
            for r in daily.itertuples()
        ],
        anomaly_c=compute_anomaly(daily),
    )

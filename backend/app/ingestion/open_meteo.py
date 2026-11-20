import asyncio
import logging
from datetime import datetime

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def fetch_hourly(
    client: httpx.AsyncClient, latitude: float, longitude: float, past_days: int = 2
) -> dict:
    """Fetch hourly temperature and humidity from Open-Meteo (UTC), with simple retries."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m",
        "timezone": "UTC",
        "past_days": past_days,
        "forecast_days": 1,
    }
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = await client.get(get_settings().open_meteo_url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            last_error = exc
            logger.warning("Open-Meteo attempt %s failed: %s", attempt + 1, exc)
            await asyncio.sleep(2**attempt)
    raise RuntimeError("Open-Meteo request failed after 3 attempts") from last_error


def parse_hourly(payload: dict, until: datetime | None = None) -> list[dict]:
    """Turn an Open-Meteo response into rows, skipping gaps and (optionally) future hours."""
    hourly = payload.get("hourly") or {}
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    humidity = hourly.get("relative_humidity_2m", [])

    rows: list[dict] = []
    for i, stamp in enumerate(times):
        temp = temps[i] if i < len(temps) else None
        if temp is None:
            continue
        observed_at = datetime.fromisoformat(stamp)
        if until is not None and observed_at > until:
            continue
        hum = humidity[i] if i < len(humidity) else None
        rows.append(
            {
                "observed_at": observed_at,
                "temperature_c": float(temp),
                "humidity_pct": float(hum) if hum is not None else None,
            }
        )
    return rows

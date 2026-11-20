"""Heat metrics. Pure functions (no DB, no HTTP) so they are easy to test."""
import math
from collections.abc import Iterable

import pandas as pd


def c_to_f(c: float) -> float:
    return c * 9 / 5 + 32


def f_to_c(f: float) -> float:
    return (f - 32) * 5 / 9


def _missing(value: float | None) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def heat_index_c(temp_c: float, humidity_pct: float | None) -> float:
    """US National Weather Service heat index (Rothfusz regression), in °C.

    Falls back to the plain temperature when humidity is unknown.
    """
    if _missing(humidity_pct):
        return round(temp_c, 1)

    t = c_to_f(temp_c)
    rh = float(humidity_pct)

    # Steadman's simple formula; fine for milder conditions.
    simple = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)
    if (simple + t) / 2 < 80.0:
        return round(f_to_c(simple), 1)

    hi = (
        -42.379
        + 2.04901523 * t
        + 10.14333127 * rh
        - 0.22475541 * t * rh
        - 0.00683783 * t * t
        - 0.05481717 * rh * rh
        + 0.00122874 * t * t * rh
        + 0.00085282 * t * rh * rh
        - 0.00000199 * t * t * rh * rh
    )
    if rh < 13 and 80 <= t <= 112:
        hi -= ((13 - rh) / 4) * math.sqrt((17 - abs(t - 95)) / 17)
    elif rh > 85 and 80 <= t <= 87:
        hi += ((rh - 85) / 10) * ((87 - t) / 5)
    return round(f_to_c(hi), 1)


def heat_category(hi_c: float) -> str:
    """NWS heat-index risk bands, converted to °C."""
    if hi_c < 27:
        return "normal"
    if hi_c < 32:
        return "caution"
    if hi_c < 39:
        return "extreme_caution"
    if hi_c < 51:
        return "danger"
    return "extreme_danger"


def heat_index_series(temp: Iterable[float], humidity: Iterable[float | None]) -> list[float]:
    return [heat_index_c(t, h) for t, h in zip(temp, humidity, strict=True)]


DAILY_COLUMNS = ["date", "temp_min_c", "temp_max_c", "temp_mean_c", "heat_index_max_c"]


def build_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Hourly rows -> one row per UTC day.

    Expects columns: observed_at, temperature_c, humidity_pct.
    """
    if df.empty:
        return pd.DataFrame(columns=DAILY_COLUMNS)

    data = df.copy()
    data["heat_index_c"] = heat_index_series(data["temperature_c"], data["humidity_pct"])
    data["date"] = pd.to_datetime(data["observed_at"]).dt.date
    daily = (
        data.groupby("date")
        .agg(
            temp_min_c=("temperature_c", "min"),
            temp_max_c=("temperature_c", "max"),
            temp_mean_c=("temperature_c", "mean"),
            heat_index_max_c=("heat_index_c", "max"),
        )
        .reset_index()
        .round(1)
    )
    return daily


def compute_anomaly(daily: pd.DataFrame, min_baseline_days: int = 7) -> float | None:
    """Latest daily mean minus the mean of the earlier days, in °C.

    Returns None when there are not enough earlier days to form a baseline.
    Note: the latest day may be partial, which slightly biases the result.
    """
    if len(daily) <= min_baseline_days:
        return None
    ordered = daily.sort_values("date")
    latest = float(ordered["temp_mean_c"].iloc[-1])
    baseline = float(ordered["temp_mean_c"].iloc[:-1].mean())
    return round(latest - baseline, 1)

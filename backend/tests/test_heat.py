import pandas as pd
import pytest

from app.services.heat import (
    build_daily_summary,
    compute_anomaly,
    f_to_c,
    heat_category,
    heat_index_c,
)


def test_heat_index_matches_nws_chart_hot_humid():
    # NWS chart: 90°F at 70% humidity feels like about 106°F
    assert heat_index_c(f_to_c(90), 70) == pytest.approx(f_to_c(106), abs=1.0)


def test_heat_index_mild_is_close_to_temperature():
    assert heat_index_c(f_to_c(80), 40) == pytest.approx(f_to_c(80), abs=1.0)


def test_heat_index_without_humidity_returns_temperature():
    assert heat_index_c(33.04, None) == 33.0
    assert heat_index_c(33.04, float("nan")) == 33.0


def test_humidity_raises_heat_index():
    assert heat_index_c(34, 80) > heat_index_c(34, 30)


@pytest.mark.parametrize(
    ("hi", "expected"),
    [(20, "normal"), (28, "caution"), (35, "extreme_caution"), (45, "danger"), (55, "extreme_danger")],
)
def test_heat_category_bands(hi, expected):
    assert heat_category(hi) == expected


def _hourly_frame(days: int, temp: float = 30.0) -> pd.DataFrame:
    stamps = pd.date_range("2026-11-01", periods=24 * days, freq="h")
    return pd.DataFrame(
        {"observed_at": stamps, "temperature_c": temp, "humidity_pct": 50.0}
    )


def test_daily_summary_one_row_per_day():
    daily = build_daily_summary(_hourly_frame(3))
    assert len(daily) == 3
    assert {"temp_min_c", "temp_max_c", "temp_mean_c", "heat_index_max_c"} <= set(daily.columns)


def test_daily_summary_empty_input():
    empty = pd.DataFrame(columns=["observed_at", "temperature_c", "humidity_pct"])
    assert build_daily_summary(empty).empty


def test_anomaly_needs_enough_history():
    assert compute_anomaly(build_daily_summary(_hourly_frame(5))) is None


def test_anomaly_detects_hot_latest_day():
    frame = _hourly_frame(9, temp=30.0)
    frame.loc[frame.index[-24:], "temperature_c"] = 36.0
    assert compute_anomaly(build_daily_summary(frame)) == pytest.approx(6.0, abs=0.1)

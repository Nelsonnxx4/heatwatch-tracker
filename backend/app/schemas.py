import datetime as dt

from pydantic import BaseModel, ConfigDict


class CityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    state: str
    country: str
    latitude: float
    longitude: float


class ObservationOut(BaseModel):
    observed_at: dt.datetime
    temperature_c: float
    humidity_pct: float | None
    wind_speed_kmh: float | None
    wind_direction_deg: float | None
    heat_index_c: float
    heat_category: str


class DailyOut(BaseModel):
    day: dt.date
    temp_min_c: float
    temp_max_c: float
    temp_mean_c: float
    heat_index_max_c: float


class HeatSummaryOut(BaseModel):
    city: CityOut
    current: ObservationOut
    days: list[DailyOut]
    anomaly_c: float | None


class RankingItem(BaseModel):
    city: CityOut
    heat_index_max_c: float
    heat_category: str

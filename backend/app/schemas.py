import datetime as dt

from pydantic import BaseModel, ConfigDict


class CityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    state: str
    latitude: float
    longitude: float


class ObservationOut(BaseModel):
    observed_at: dt.datetime
    temperature_c: float
    humidity_pct: float | None
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
    # Latest daily mean minus the mean of earlier days in the window.
    # None until there are enough days to compare against.
    anomaly_c: float | None


class RankingItem(BaseModel):
    city: CityOut
    heat_index_max_c: float
    heat_category: str

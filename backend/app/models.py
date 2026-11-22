from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    state: Mapped[str] = mapped_column(String(64))
    country: Mapped[str] = mapped_column(String(64), default="Nigeria")
    latitude: Mapped[float]
    longitude: Mapped[float]


class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (UniqueConstraint("city_id", "observed_at", name="uq_city_time"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), index=True)
    observed_at: Mapped[datetime] = mapped_column(index=True)
    temperature_c: Mapped[float]
    humidity_pct: Mapped[float | None]
    wind_speed_kmh: Mapped[float | None]
    wind_direction_deg: Mapped[float | None]

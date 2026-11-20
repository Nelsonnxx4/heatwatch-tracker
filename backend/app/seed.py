from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import City

CITIES = [
    ("abuja", "Abuja", "FCT", 9.0765, 7.3986),
    ("lagos", "Lagos", "Lagos", 6.5244, 3.3792),
    ("kano", "Kano", "Kano", 12.0022, 8.5919),
    ("port-harcourt", "Port Harcourt", "Rivers", 4.8156, 7.0498),
    ("makurdi", "Makurdi", "Benue", 7.7337, 8.5214),
    ("maiduguri", "Maiduguri", "Borno", 11.8333, 13.15),
    ("enugu", "Enugu", "Enugu", 6.4584, 7.5464),
    ("ibadan", "Ibadan", "Oyo", 7.3775, 3.9470),
]


async def seed_cities(session: AsyncSession) -> int:
    """Insert any missing cities. Safe to run repeatedly."""
    existing = set((await session.scalars(select(City.slug))).all())
    new = [
        City(slug=slug, name=name, state=state, latitude=lat, longitude=lon)
        for slug, name, state, lat, lon in CITIES
        if slug not in existing
    ]
    session.add_all(new)
    await session.commit()
    return len(new)

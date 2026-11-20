from datetime import UTC, datetime


def to_naive_utc(value: datetime) -> datetime:
    """Normalise any datetime to naive UTC, the format stored in the DB."""
    if value.tzinfo is not None:
        return value.astimezone(UTC).replace(tzinfo=None)
    return value

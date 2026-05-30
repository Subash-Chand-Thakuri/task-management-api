from datetime import UTC, datetime


def to_naive_utc(value: datetime | None) -> datetime | None:
    """Convert aware datetimes to naive UTC for TIMESTAMP WITHOUT TIME ZONE columns."""
    if value is None or value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)

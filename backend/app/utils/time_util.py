from __future__ import annotations

from datetime import datetime, timezone


def now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def dt_to_ms(value: datetime | None) -> int | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return int(value.timestamp() * 1000)


def ms_to_dt(value: int | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc)


def ms_to_date_key(value: int) -> str:
    return ms_to_dt(value).strftime("%Y-%m-%d")


def days_ago_ms(days: int) -> int:
    return now_ms() - days * 86_400_000


def hours_ago_ms(hours: int) -> int:
    return now_ms() - hours * 3_600_000

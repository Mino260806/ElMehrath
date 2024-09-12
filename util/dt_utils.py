from datetime import datetime, timezone


def to_utc(dt):
    return dt.astimezone(tz=timezone.utc)

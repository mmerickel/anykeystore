from datetime import timedelta

def coerce_timedelta(value):
    if isinstance(value, timedelta):
        return value
    if isinstance(value, int) or isinstance(value, float):
        return timedelta(seconds=value)

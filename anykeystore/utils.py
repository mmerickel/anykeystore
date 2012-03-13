from datetime import timedelta

def coerce_timedelta(value):
    if isinstance(value, timedelta):
        return value
    if isinstance(value, int) or isinstance(value, float):
        return timedelta(seconds=value)

def splitlines(s):
    return list(filter(None, [c.strip() for x in s.splitlines()
                                        for c in x.split(', ')]))

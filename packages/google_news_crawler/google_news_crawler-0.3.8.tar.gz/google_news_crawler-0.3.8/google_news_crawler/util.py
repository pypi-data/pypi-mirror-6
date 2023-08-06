from datetime import datetime
import pytz


def now():
    """Return th current time as a `datetime` object with the timezone set
    to UTC (`pytz.utc`)"""
    return datetime.now(pytz.utc)

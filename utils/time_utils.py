import datetime
import time


def to_unix(date):
    return long(time.mktime(date.timetuple()) * 1000.0)


def from_unix(timestamp):
    return datetime.datetime.fromtimestamp(timestamp / 1000.0)

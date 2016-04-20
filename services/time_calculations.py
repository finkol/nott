from datetime import datetime, timedelta


def time_plus(time, timedelta):
    start = datetime(
        2000, 1, 1,
        hour=time.hour, minute=time.minute, second=time.second)
    end = start + timedelta
    return end.time()


def perdelta_time(start, end, delta):
    curr = start
    while curr != end:
        yield curr
        curr = time_plus(curr, delta)


def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta


def minutes_to_hours_minutes(minutes):
    minutes = timedelta(minutes=minutes)
    d = datetime(1, 1, 1) + minutes

    return "%02d:%02d" % (d.hour, d.minute)


def seconds_to_hours_minutes(seconds):
    sec = timedelta(seconds=seconds)
    d = datetime(1, 1, 1) + sec

    return "%02d:%02d" % (d.hour, d.minute)


def seconds_to_hours_minutes_verbal(seconds):
    sec = timedelta(seconds=seconds)
    d = datetime(1, 1, 1) + sec

    if d.hour == 0:
        return "%2d min" % d.minute
    elif d.hour == 1:
        return "%2d hr, %2d min" % (d.hour, d.minute)
    else:
        return "%2d hrs, %2d min" % (d.hour, d.minute)

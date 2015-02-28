from datetime import datetime


def now():
    return datetime.utcnow().replace(microsecond=0)

def timestamp(time):
    unixEpoch = datetime.utcfromtimestamp(0)
    return int((time - unixEpoch).total_seconds())

def timeDeltaString(date1, date2):
    delta = date1 - date2
    dayString = "{} day{}".format(delta.days, "" if delta.days == 1 else "s")
    hours = delta.seconds // 3600
    hourString = "{} hour{}".format(hours, "" if hours == 1 else "s")
    minutes = (delta.seconds // 60) % 60
    minuteString = "{} minute{}".format(minutes, "" if minutes == 1 else "s")
    return "{}, {} and {}".format(dayString, hourString, minuteString)

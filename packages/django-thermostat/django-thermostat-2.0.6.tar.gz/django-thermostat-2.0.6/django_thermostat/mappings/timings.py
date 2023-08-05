from time import strftime, localtime, mktime, strptime
from astral import Location#, AstralGeocoder
import datetime
from django.conf import settings
from pytz import timezone


def current_day_of_week(mo=None):

    return strftime("%a", localtime())


def current_month(mo=None):
    return strftime("%m", localtime())


def current_year(mo=None):
    return strftime("%Y", localtime())


def current_day_of_month(mo=None):
    return strftime("%d", localtime())


def current_time(mo=None):
    lt = localtime()
    st = "%s %s %s %s:%s:%s" %(
        strftime("%d", lt),
        strftime("%m", lt),
        strftime("%Y", lt),
        strftime("%H", lt),
        strftime("%M", lt),
        strftime("%S", lt))
    t = strptime(st, "%d %m %Y %H:%M:%S")
    return mktime(t)



def is_weekend(mo=None):
    today = current_day_of_week()
    if today == "Sat" or today == "Sun":
        return 1
    return 0


def is_at_night(mo=None):
    a = Location()
    a.timezone = settings.TIME_ZONE

    #sunrise = mktime(strptime(a.sunrise(), "%Y-%m-%d %H:%M:%S")) #2013-12-13 22:57:02
    sunset = mktime(strptime(a.sunset().strftime("%a %b %d %H:%M:%S %Y", )))
    sunrise = mktime(strptime(a.sunrise().strftime("%a %b %d %H:%M:%S %Y", )))

    lt = localtime()

    if localtime() > sunset and localtime() < sunrise:
        return True
    return False


mappings = [
    current_day_of_week,
    current_time,
    is_weekend,
    current_month,
    current_day_of_month,
    current_year,
    is_at_night,
    ]

from time import strftime, localtime, mktime, strptime
from astral import Location#, AstralGeocoder
import datetime, logging
from django.conf import settings as dsettings
import django_thermostat.settings as settings
import pytz
from dateutil.parser import parse


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
    a.timezone = dsettings.TIME_ZONE
    tz = pytz.timezone(a.timezone)
    #Tue, 22 Jul 2008 08:17:41 +0200
    #Sun, 26 Jan 2014 17:39:49 +01:00
    a_sunset = a.sunset()
    
    a_sunrise = a.sunrise()
      
    n = datetime.datetime.now()
    n = tz.localize(n)
    logging.debug("NOW: %s; sunrise: %s; dif: %s"  % (n, a_sunrise, n - a_sunrise))
    logging.debug("NOW: %s; sunset: %s; dif: %s" % (n, a_sunset, n - a_sunset))
    passed_sunrise = (n - a_sunrise) > datetime.timedelta(minutes=settings.MINUTES_AFTER_SUNRISE_FOR_DAY)
    logging.debug("Passed %s sunrise more than %s minutes" % (passed_sunrise, settings.MINUTES_AFTER_SUNRISE_FOR_DAY))
    passed_sunset = (n - a_sunset) > datetime.timedelta(minutes=settings.MINUTES_AFTER_SUNSET_FOR_DAY)
    logging.debug("Passed %s sunset more than %s minutes" % (passed_sunset, settings.MINUTES_AFTER_SUNSET_FOR_DAY))
    if not passed_sunrise or passed_sunset:
        return True
    if passed_sunrise and not passed_sunset:
        return False    
    return True


mappings = [
    current_day_of_week,
    current_time,
    is_weekend,
    current_month,
    current_day_of_month,
    current_year,
    is_at_night,
    ]

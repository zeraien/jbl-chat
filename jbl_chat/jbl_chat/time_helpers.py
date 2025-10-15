import datetime
import math
import typing
from datetime import time, timedelta
from numbers import Number
from string import Template

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _

import pytz


def replace_time(dt: datetime, t: time) -> datetime:
    return dt.replace(
        hour=t.hour,
        minute=t.minute,
        second=t.second,
        microsecond=t.microsecond,
    )


def combine_date_and_time(
    date_obj: datetime.date, time_obj: datetime.time, tzname: str = None
) -> datetime.datetime | None:
    if None in (time_obj, date_obj):
        return None
    dt = datetime.datetime(
        year=date_obj.year,
        month=date_obj.month,
        day=date_obj.day,
        hour=time_obj.hour,
        minute=time_obj.minute,
        second=time_obj.second,
        microsecond=time_obj.microsecond,
    )
    if tzname:
        if isinstance(tzname, str):
            tz = pytz.timezone(tzname)
        else:
            tz = tzname
        dt = tz.localize(dt)
    return dt


def get_noon(dt_obj: datetime.date, add_days: int = 0, utc: bool = False):
    tz = timezone.utc if utc else timezone.get_current_timezone()
    noon = timezone.datetime(dt_obj.year, dt_obj.month, dt_obj.day, 12) + timedelta(
        days=add_days
    )
    return tz.localize(noon)


def end_of_day(date_obj: datetime.date, add_days: int = 0, utc: bool = False):
    """
    take a date object and return the same date in the guise of a
    datetime at 23:59 in the current timezone
    :param add_days: how many days to add or subtract, default 0
    :param date_obj: a date
    :param utc: return a UTC timestamp
    :return:
    """
    almost_midnight = timezone.datetime(
        date_obj.year, date_obj.month, date_obj.day, 23, 59
    ) + timedelta(days=add_days)
    return timezone.make_aware(almost_midnight, timezone=pytz.UTC if utc else None)


def get_midnight(dt_obj: timezone.datetime, add_days: int = 0) -> timezone.datetime:
    tz = timezone.get_current_timezone()
    midnight = timezone.datetime(dt_obj.year, dt_obj.month, dt_obj.day) + timedelta(
        days=add_days
    )
    return tz.localize(midnight)


def prepare_duration(sec: int) -> dict:
    is_negative = sec < 0
    sec = math.fabs(sec)

    minutes, seconds = divmod(sec, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    days, hours, minutes, seconds = [int(d) for d in [days, hours, minutes, seconds]]
    return {
        "is_negative": is_negative,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }


def pretty_duration(
    time_delta: timedelta | int | None, show_seconds: bool = False
) -> str:
    if isinstance(time_delta, timedelta):
        time_delta = time_delta.total_seconds()
    if not isinstance(time_delta, Number):
        return ""
    timedata = prepare_duration(time_delta)

    days = timedata["days"]
    hours = timedata["hours"]
    minutes = timedata["minutes"]
    seconds = timedata["seconds"]

    if not show_seconds:
        if days > 0:
            if hours == 0 and minutes == 0:
                return _("%(days)sd") % timedata
            elif minutes == 0:
                return _("%(days)sd %(hours)sh") % timedata
            else:
                return _("%(days)sd %(hours)sh %(minutes)smin") % timedata
        elif hours > 0:
            if minutes == 0:
                return _("%(hours)sh") % timedata
            else:
                return _("%(hours)sh %(minutes)smin") % timedata
        elif minutes > 0:
            return _("%(minutes)smin") % timedata
        elif seconds > 0:
            return _("%(seconds)ss") % timedata
        else:
            return "0"
    else:
        if days > 0:
            return _("%(days)sd %(hours)sh %(minutes)smin %(seconds)ss") % timedata
        elif hours > 0:
            return _("%(hours)sh %(minutes)smin %(seconds)ss") % timedata
        elif minutes > 0:
            return _("%(minutes)smin %(seconds)ss") % timedata
        elif seconds > 0:
            return _("%(seconds)ss") % timedata
        else:
            return "0"


def to_epoch(
    dt: typing.Union[datetime.datetime, datetime.date, str],
    return_none: bool = False,
    return_int: bool = True,
) -> typing.Optional[int | float]:
    """Return the number of seconds since the epoch in UTC.
    If a naive datetime object is passed, it is assumed to be in UTC!

    Accepts strings in the following datetime format (YYYY-MM-DD HH:MM)
    or a datetime object.

       :param return_int: rounds it to the nearest second
       :param dt: Datetime object or string
       :param return_none:  if `dt` is invalid, return None if this is true,
       otherwise return 0
       :return: the epoch seconds as an `int`
    """

    if isinstance(dt, str):
        try:
            dt = datetime.datetime.strptime(dt, settings.PY_DATETIME_FORMAT)
        except (TypeError, AttributeError, ValueError):
            return 0
    elif isinstance(dt, int):
        return dt
    elif not hasattr(dt, "timestamp"):
        dt = None

    if dt is None:
        if return_none:
            return None
        else:
            return 0
    else:
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.utc)
        t = dt.timestamp()
        if return_int:
            return int(round(t))
        else:
            return t


def from_epoch(epo: int | float) -> datetime.datetime:
    """
    :param epo: epoc seconds (UTC) to turn into a `datetime.datetime` object
    :return: Datetime object
    """
    if epo is None:
        epo = 0
    return timezone.make_aware(datetime.datetime.utcfromtimestamp(epo), timezone.utc)


def strfdelta(tdelta, fmt):
    class DeltaTemplate(Template):
        delimiter = "%"

    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = "{:02d}".format(hours)
    d["M"] = "{:02d}".format(minutes)
    d["S"] = "{:02d}".format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


def parse_date_text(text: str) -> datetime.date:
    return datetime.datetime.strptime(text, "%Y-%m-%d").date()


def date_range_str(start: datetime.date | None, end: datetime.date | None) -> str:
    def date_str(d: datetime.date | None, sep="-", default="-") -> str:
        fmt = f"%Y{sep}%m{sep}%d"
        return f"{d.strftime(fmt) if d else default}"

    return f"{date_str(start)} to {date_str(end)}"

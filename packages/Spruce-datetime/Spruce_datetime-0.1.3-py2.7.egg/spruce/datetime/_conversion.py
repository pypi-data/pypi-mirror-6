"""Conversions."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from calendar import timegm as _timegm
from datetime import datetime as _datetime
import os as _os
from time import mktime as _mktime

import pytz as _tz

from . import _tz as _tz_local


def datetime_from_localtime_structtime(struct_time):
    """
    Convert a local-time :class:`~time.struct_time` to a UTC
    :class:`~datetime.datetime`.

    The input is assumed to be in local time.  The resulting
    :class:`~datetime.datetime` is in UTC and is time zone aware.

    :param struct_time:
        A time struct.
    :type struct_time: :class:`time.struct_time`

    :rtype: :class:`datetime.datetime`

    """
    return datetime_from_unixtime(_mktime(struct_time))


def datetime_from_structtime(struct_time):
    """
    Convert a UTC :class:`~time.struct_time` to a UTC
    :class:`~datetime.datetime`.

    The input is assumed to be in UTC.  The resulting
    :class:`~datetime.datetime` is in UTC and is time zone aware.

    :param struct_time:
        A time struct.
    :type struct_time: :class:`time.struct_time`

    :rtype: :class:`datetime.datetime`

    """
    return naive_datetime_from_structtime(struct_time)\
            .replace(tzinfo=_tz.UTC)


def datetime_from_unixtime(unixtime):
    """Convert a Unix time to a UTC :class:`~datetime.datetime`.

    Unix time is defined in UTC.  The resulting :class:`~datetime.datetime`
    is in UTC and is time zone aware.

    :param int unixtime:
        A time struct.

    :rtype: :class:`datetime.datetime`

    """
    return _datetime.fromtimestamp(unixtime, _tz.UTC)


def datetime_with_named_tz(dt, tzname):

    """Assign a named time zone to a date and time.

    .. warning::
        This function will go away after the relevant bug is fixed in
        :mod:`pytz`.

    This works around a bug in :mod:`pytz` (from :pypi:`pytz`) when it comes
    to handling time zones that consist of DST and non-DST counterparts.

    If the :mod:`pytz` bug was fixed, then this would be equivalent to

    .. parsed-literal::

        *dt*.replace(tzinfo=pytz.timezone(*tzname*))

    :param dt:
        A date and time.
    :type dt: :class:`datetime.datetime`

    :param str tzname:
        The name of a time zone.  One of the relative file paths under
        :file:`/usr/share/zoneinfo/`.

    :rtype: :class:`datetime.datetime`

    """

    _os.environ['TZ'] = tzname
    _tz_local.tzset()

    tz = _tz.FixedOffset(_tz_local.LOCALTIME.utcoffset(dt).total_seconds()
                         / 60)
    dt_withtz = dt.replace(tzinfo=tz)

    del _os.environ['TZ']
    _tz_local.tzset()

    return dt_withtz


def localtime_datetime_from_localtime_structtime(struct_time):
    """
    Convert a local-time :class:`~time.struct_time` to a local-time
    :class:`~datetime.datetime`.

    The input is assumed to be in local time.  The resulting
    :class:`~datetime.datetime` is in local time and is time zone aware.

    :param struct_time:
        A time struct.
    :type struct_time: :class:`time.struct_time`

    :rtype: :class:`datetime.datetime`

    """
    return naive_datetime_from_structtime(struct_time)\
            .replace(tzinfo=_tz_local.LOCALTIME)


def localtime_datetime_from_unixtime(unixtime):
    """Convert a Unix time to a local-time :class:`~datetime.datetime`.

    Unix time is defined in UTC.  The resulting :class:`~datetime.datetime`
    is in local time and is time zone aware.

    :param int unixtime:
        A time struct.

    :rtype: :class:`datetime.datetime`

    """
    return _datetime.fromtimestamp(unixtime, _tz_local.LOCALTIME)


def naive_datetime_from_structtime(struct_time):
    """
    Convert a :class:`~time.struct_time` to a naive
    :class:`~datetime.datetime`.

    The input and the result express the same time in the same time zone,
    but that time zone is not specified.  Consequently, the resulting
    :class:`~datetime.datetime` is not time zone aware.

    :param struct_time:
        A time struct.
    :type struct_time: :class:`time.struct_time`

    :rtype: :class:`datetime.datetime`

    """
    return _datetime(year=struct_time.tm_year, month=struct_time.tm_mon,
                     day=struct_time.tm_mday, hour=struct_time.tm_hour,
                     minute=struct_time.tm_min, second=struct_time.tm_sec)


def unixtime_from_datetime(datetime):
    """Convert a :class:`datetime.datetime` to a Unix time.

    If the *datetime* is time zone aware, then it is converted to UTC before
    being converted to Unix time.  Otherwise it is converted directly to
    Unix time, regardless of the value of :samp:`{datetime}.dst()`; in this
    case, it is up to the caller to ensure that *datetime* is in UTC.

    :param dt:
        A date and time.
    :type dt: :class:`datetime.datetime`

    :rtype: :obj:`int`

    """
    return _timegm(datetime.utctimetuple())

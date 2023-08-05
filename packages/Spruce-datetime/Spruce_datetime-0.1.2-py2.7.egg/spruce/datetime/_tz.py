"""Time zones.

See :mod:`pytz` from :pypi:`pytz` for :class:`~datetime.tzinfo` objects
for other time zones.

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from datetime import timedelta as _timedelta, tzinfo as _tzinfo
import time as _localtime
from time \
    import mktime as _timestruct_to_unixtime, \
           localtime as _unixtime_to_localtimestruct, \
           tzset as _tzset


_TIMEDELTA_ZERO = _timedelta(0)


def tzset():

    """
    Reset the local time conversion rules per environment variable
    :envvar:`TZ`.

    .. seealso:: :func:`time.tzset`

    """

    _tzset()

    global _TIMEDELTA_DST, _TIMEDELTA_DSTSTD, _TIMEDELTA_STD
    _TIMEDELTA_STD = _timedelta(seconds=-_localtime.timezone)
    if _localtime.daylight:
        _TIMEDELTA_DST = _timedelta(seconds=-_localtime.altzone)
    else:
        _TIMEDELTA_DST = _TIMEDELTA_STD
    _TIMEDELTA_DSTSTD = _TIMEDELTA_DST - _TIMEDELTA_STD

tzset()


class _LocalTime(_tzinfo):

    def utcoffset(self, datetime):
        if self._isdst(datetime):
            return _TIMEDELTA_DST
        else:
            return _TIMEDELTA_STD

    def dst(self, datetime):
        if self._isdst(datetime):
            return _TIMEDELTA_DSTSTD
        else:
            return _TIMEDELTA_ZERO

    def tzname(self, datetime):
        return _localtime.tzname[self._isdst(datetime)]

    def _isdst(self, datetime):
        timetuple = (datetime.year, datetime.month, datetime.day,
                     datetime.hour, datetime.minute, datetime.second,
                     datetime.weekday(), 0, 0)
        unixtime = _timestruct_to_unixtime(timetuple)
        timetuple = _unixtime_to_localtimestruct(unixtime)
        return timetuple.tm_isdst > 0
LOCALTIME = _LocalTime()
"""A :class:`datetime.tzinfo` that represents local time.

Adapted from the example `tzinfo objects
<http://docs.python.org/library/datetime.html#tzinfo-objects>`_.

"""

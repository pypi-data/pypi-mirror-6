"""Miscellaneous tools."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from datetime import datetime as _datetime

import pytz as _tz

from . import _tz as _tz_local


def now():
    """The current date and time in UTC.

    The resulting :class:`~datetime.datetime` is time zone aware, unlike
    :meth:`datetime.datetime.utcnow`.

    :rtype: :class:`datetime.datetime`

    """
    return _datetime.now(_tz.UTC)


def now_localtime():
    """The current date and time in local time.

    The resulting :class:`~datetime.datetime` is time zone aware, unlike
    :meth:`~datetime.datetime.now` called with no argument.

    :rtype: :class:`datetime.datetime`

    """
    return _datetime.now(_tz_local.LOCALTIME)

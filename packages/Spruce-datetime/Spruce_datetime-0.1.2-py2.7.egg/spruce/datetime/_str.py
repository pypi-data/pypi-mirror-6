"""String formats and representations."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from datetime import datetime as _datetime
from itertools import chain as _chain
import re as _re

import pytz as _tz


RFC2822_MONTH_ABBRS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                       'Sep', 'Oct', 'Nov', 'Dec']

RFC2822_MONTH_ABBRS_RE = _re.compile('|'.join(RFC2822_MONTH_ABBRS))

RFC2822_OBSOLETE_MONTH_NAMES = ['January', 'February', 'March', 'April', 'May',
                                'June', 'July', 'August', 'September',
                                'October', 'November', 'December']

RFC2822_OBSOLETE_MONTH_NAMES_RE = \
    _re.compile('|'.join(RFC2822_OBSOLETE_MONTH_NAMES))

RFC2822_OBSOLETE_TZ_HOURS_BY_NAME = {'UT': 0,
                                     'GMT': 0,
                                     'EDT': -4,
                                     'EST': -5,
                                     'CDT': -5,
                                     'CST': -6,
                                     'MDT': -6,
                                     'MST': -7,
                                     'PDT': -7,
                                     'PST': -8,
                                     }
for military_tz_name in (chr(ord_) for ord_ in _chain(range(65, 74),
                                                      range(75, 91),
                                                      range(97, 106),
                                                      range(107, 122))):
    RFC2822_OBSOLETE_TZ_HOURS_BY_NAME[military_tz_name] = 0

RFC2822_OBSOLETE_TZ_NAMES_RE = \
    _re.compile('|'.join(RFC2822_OBSOLETE_TZ_HOURS_BY_NAME.keys()))

RFC2822_OBSOLETE_WEEKDAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                                  'Friday', 'Saturday', 'Sunday']

RFC2822_OBSOLETE_WEEKDAY_NAMES_RE = \
    _re.compile('|'.join(RFC2822_OBSOLETE_WEEKDAY_NAMES))

RFC2822_WEEKDAY_ABBRS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

RFC2822_WEEKDAY_ABBRS_RE = _re.compile('|'.join(RFC2822_WEEKDAY_ABBRS))


CTIME_FORMAT_RE = \
    _re.compile(r'(?P<weekday_abbr>{}) (?P<month_abbr>{})'
                    .format(RFC2822_WEEKDAY_ABBRS_RE.pattern,
                            RFC2822_MONTH_ABBRS_RE.pattern)
                + r' (?: ?(?P<day>((?<! )[1-3])?\d))'
                  r' (?P<hour>[0-2]\d):(?P<minute>[0-5]\d):(?P<second>[0-5]\d)'
                  r' (?P<year>\d\d\d\d)')


RFC1123_FORMAT_RE = \
    _re.compile(r'(?:(?P<weekday_abbr>{})|(?P<obsolete_weekday_name>{})),'
                    .format(RFC2822_WEEKDAY_ABBRS_RE.pattern,
                            RFC2822_OBSOLETE_WEEKDAY_NAMES_RE.pattern)
                + r' (?P<day>[0-3]\d)'
                + r' (?:(?P<month_abbr>{})|(?P<obsolete_month_name>{}))'
                      .format(RFC2822_MONTH_ABBRS_RE.pattern,
                              RFC2822_OBSOLETE_MONTH_NAMES_RE.pattern)
                + r' (?P<year>\d\d\d\d)'
                + r' (?P<hour>[0-2]\d):(?P<minute>[0-5]\d):(?P<second>[0-5]\d)'
                  r' (?P<tz>(?:(?P<tz_sign>[-+])(?P<tz_hours>\d\d)'
                  r'(?P<tz_minutes>[0-5]\d))'
                  r'|(?P<obsolete_tz_name>{}))'
                      .format(RFC2822_OBSOLETE_TZ_NAMES_RE.pattern))


HTTP11_RFC1123_FORMAT_RE = \
    _re.compile(r'(?P<weekday_abbr>{}), (?P<day>[0-3]\d)'
                    .format(RFC2822_WEEKDAY_ABBRS_RE.pattern)
                + r' (?P<month_abbr>{}) (?P<year>\d\d\d\d)'
                      .format(RFC2822_MONTH_ABBRS_RE.pattern)
                + r' (?P<hour>[0-2]\d):(?P<minute>[0-5]\d):(?P<second>[0-5]\d)'
                  r' GMT')


HTTP11_RFC850_FORMAT_RE = \
    _re.compile(r'(?P<obsolete_weekday_name>{}),'
                    .format(RFC2822_WEEKDAY_ABBRS_RE.pattern,
                            RFC2822_OBSOLETE_WEEKDAY_NAMES_RE.pattern)
                + r' (?P<day>[0-3]\d)-(?P<obsolete_month_name>{})'
                      .format(RFC2822_OBSOLETE_MONTH_NAMES_RE.pattern)
                + r' (?P<year>\d\d\d\d)'
                + r' (?P<hour>[0-2]\d):(?P<minute>[0-5]\d):(?P<second>[0-5]\d)'
                  r' GMT')


HTTP11_FORMAT_RE = '|'.join(r'(?:{})'.format(format_re.pattern)
                            for format_re
                            in (HTTP11_RFC1123_FORMAT_RE,
                                HTTP11_RFC850_FORMAT_RE, CTIME_FORMAT_RE))


def datetime_httpstr(datetime):
    return datetime.astimezone(_tz.UTC).strftime('%a, %d %b %Y %H:%M:%S GMT')


def datetime_fromhttpstr(str):

    match = HTTP11_FORMAT_RE.match(str)

    if not match:
        raise ValueError('invalid HTTP date-and-time string {!r}; expected a'
                          ' string in one of the formats specified in RFC 2616'
                          ' section 3.3.1'
                          .format(str))

    year = match.group('year')
    day = match.group('day')
    hour = match.group('hour')
    minute = match.group('minute')
    second = match.group('second')

    month_abbr = match.group('month_abbr')
    obsolete_month_name = match.group('obsolete_month_name')
    if month_abbr:
        month = 1 + RFC2822_MONTH_ABBRS.index(month_abbr)
    elif obsolete_month_name:
        month = 1 + RFC2822_OBSOLETE_MONTH_NAMES.index(obsolete_month_name)
    else:
        assert False

    if match.group('tz'):
        tz_sign = match.group('tz_sign')
        if tz_sign:
            try:
                tz_hours = int(tz_sign + match.group('tz_hours'))
                tz_minutes = int(tz_sign
                                 + (match.group('tz_minutes') or '0'))
            except (TypeError, ValueError):
                # FIXME
                raise ValueError()
            tz_minutes += tz_hours * 60

            tzinfo = _tz.FixedOffset(tz_minutes)

        else:
            obsolete_tz_name = match.group('obsolete_tz_name')
            tz_hours = RFC2822_OBSOLETE_TZ_HOURS_BY_NAME[obsolete_tz_name]
            tzinfo = _tz.FixedOffset(tz_hours * 60)
    else:
        tzinfo = _tz.UTC

    return _datetime(year, month, day, hour, minute, second, tzinfo=tzinfo)

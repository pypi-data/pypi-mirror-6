# -*- coding: utf-8 -*-

from sys import version_info
from datetime import datetime, timedelta, date
from calendar import monthrange
from operator import sub, add, neg, gt, ge, lt, mul
from functools import partial

from blackskirt import DATE_FORMAT, WEEKDAYS, WEEKDAY_MON

if version_info[0] == 2:
    from string import zfill
else:
    zfill = str.zfill
    from functools import reduce


def _diff(x, y):
    return abs(sub(x, y))


def _diff_dates(date1, date2):
    return sub(date2, date1).days


def _diff_next(wd1, wd2, inclusive=False):
    diff = _diff(wd1, wd2)
    return (diff
            if partial(ge if inclusive else gt, sub(wd2, wd1), 0)() else
            sub(WEEKDAYS, diff))


def _diff_prev(wd1, wd2, inclusive=False):
    diff = _diff(wd1, wd2)
    return neg(diff
               if partial(ge if inclusive else gt, sub(wd1, wd2), 0)() else
               sub(WEEKDAYS, diff))


def _strfy(year, month, day):
    return "{year}-{month}-{day}".format(year=year,
                                         month=zfill(str(month), 2),
                                         day=zfill(str(day), 2))


def find_weekday(d, format=DATE_FORMAT):
    return datetime.strptime(d, format).isoweekday()


def type_convert(f):
    def wrap(offset, **kwargs):
        rv = f(datetime.strptime(offset, DATE_FORMAT), **kwargs)
        return rv.strftime(DATE_FORMAT)

    return wrap


def set_offset(f):
    def _to_date(dt_):
        return date(dt_.year, dt_.month, dt_.day)

    def wrap(*args, **kwargs):
        return f(*args,
                 offset=(_to_date(datetime.strptime(kwargs["offset"],
                                                    DATE_FORMAT))
                         if kwargs.get("offset") is not None else
                         date.today()))

    return wrap


@type_convert
def next(offset, weekday=WEEKDAY_MON):
    return add(offset, timedelta(days=_diff_next(offset.isoweekday(),
                                                 weekday)))


@type_convert
def prev(offset, weekday=WEEKDAY_MON):
    return add(offset, timedelta(days=_diff_prev(offset.isoweekday(),
                                                 weekday)))


@type_convert
def nearest(offset, weekday=WEEKDAY_MON):
    def _days(wd1, wd2):
        diff_next = _diff_next(wd1, wd2, inclusive=True)
        diff_prev = _diff_prev(wd1, wd2, inclusive=True)
        return diff_next if lt(abs(diff_next), abs(diff_prev)) else diff_prev

    return add(offset, timedelta(days=_days(offset.isoweekday(),
                                            weekday)))


def nth(year, month, n=1, weekday=WEEKDAY_MON):
    offset = datetime.strptime(_strfy(year, month, 1),
                               DATE_FORMAT)
    return reduce(
        add,
        (offset,
         timedelta(days=_diff_next(offset.isoweekday(),
                                   weekday,
                                   inclusive=True)),
         timedelta(days=mul(WEEKDAYS, sub(n, 1))),)
    ).strftime(DATE_FORMAT)


def last(year, month, weekday=WEEKDAY_MON):
    offset = datetime.strptime(_strfy(year, month, monthrange(year, month)[1]),
                               DATE_FORMAT)
    return add(
        offset,
        timedelta(days=_diff_prev(offset.isoweekday(),
                                  weekday,
                                  inclusive=True))
    ).strftime(DATE_FORMAT)


@set_offset
def next_date(month, day, offset=None):
    in_current_year = date(offset.year, month, day)
    return (in_current_year
            if gt(_diff_dates(offset, in_current_year), 0) else
            date(add(offset.year, 1), month, day)).isoformat()


@set_offset
def prev_date(month, day, offset=None):
    in_current_year = date(offset.year, month, day)
    return (in_current_year
            if lt(_diff_dates(offset, in_current_year), 0) else
            date(sub(offset.year, 1), month, day)).isoformat()


@set_offset
def nearest_date(month, day, offset=None):
    return min((
        date(offset.year, month, day),  # in current year
        date(add(offset.year, 1), month, day),  # in next year
        date(sub(offset.year, 1), month, day),  # in previous year
    ), key=lambda d: abs(_diff_dates(offset, d))).isoformat()

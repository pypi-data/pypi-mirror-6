# -*- coding: utf-8 -*-

from . import WEEKDAY_MON, WEEKDAY_SAT, WEEKDAY_SUN
from .lib import ops


def mondayise(d, cases=((WEEKDAY_SAT, WEEKDAY_MON),
                        (WEEKDAY_SUN, WEEKDAY_MON))):
    wd = ops.find_weekday(d)
    return ops.next(d, weekday=dict(cases)[wd]) if wd in dict(cases) else d


next_weekday = ops.next
prev_weekday = ops.prev
nearest_weekday = ops.nearest
nth_weekday = ops.nth
last_weekday = ops.last

next_date = ops.next_date
prev_date = ops.prev_date
nearest_date = ops.nearest_date

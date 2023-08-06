# -*- coding: utf-8 -*-

from functools import partial

from . import WEEKDAY_MON, WEEKDAY_TUE, WEEKDAY_SAT, WEEKDAY_SUN
from .ops import mondayise, nth_weekday

"""
1 January New Year's Day
2 January Day after New Year's Day
6 February Waitangi Day (mondayise)

The Friday before Easter Sunday Good Friday
The day after Easter Sunday Easter Monday

25 April Anzac Day (mondayise)

The first Monday in June Queen's Birthday

The fourth Monday in October Labour Day

25 December Christmas Day
26 December Boxing Day'
"""

holiday_list = {
    "NZL": (
        partial(mondayise, month=1, day=1,
                cases=((WEEKDAY_SAT, WEEKDAY_MON),
                       (WEEKDAY_SUN, WEEKDAY_MON),)),
        partial(mondayise, month=1, day=2,
                cases=((WEEKDAY_SAT, WEEKDAY_MON),
                       (WEEKDAY_SUN, WEEKDAY_TUE),)),
        partial(mondayise, month=2, day=6,
                cases=((WEEKDAY_SAT, WEEKDAY_MON),
                       (WEEKDAY_SUN, WEEKDAY_MON),)),
        partial(mondayise, month=4, day=25,
                cases=((WEEKDAY_SAT, WEEKDAY_MON),
                       (WEEKDAY_SUN, WEEKDAY_MON),)),
        partial(nth_weekday, month=6, n=1, weekday=WEEKDAY_MON),
        partial(nth_weekday, month=10, n=4, weekday=WEEKDAY_MON),
        partial(mondayise, month=12, day=25,
                cases=((WEEKDAY_SAT, WEEKDAY_MON),
                       (WEEKDAY_SUN, WEEKDAY_MON),)),
        partial(mondayise, month=12, day=26,
                cases=((WEEKDAY_SAT, WEEKDAY_MON),
                       (WEEKDAY_SUN, WEEKDAY_TUE),)),
    )
}


def holidays(tricode, year):
    pass

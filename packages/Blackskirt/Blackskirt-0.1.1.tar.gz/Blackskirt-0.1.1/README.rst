Blackskirt
==========
Relative weekday/date utilities useful for finding public holidays

Installation
------------
.. code-block:: bash

    pip install blackskirt

After installation is complete, try the following import statements to
make sure it's working.

.. code-block:: python

    from blackskirt import (WEEKDAY_MON, WEEKDAY_TUE, WEEKDAY_WED,
                            WEEKDAY_THU, WEEKDAY_FRI, WEEKDAY_SAT,
                            WEEKDAY_SUN,)
    from blackskirt.ops import (mondayise, next_weekday, prev_weekday,
                                nearest_weekday, nth_weekday, last_weekday,
                                next_date, prev_date, nearest_date,)

Examples
--------
``mondayise``
~~~~~~~~~~~~~
1. New Year's Day: 1 January (or the following Monday if it falls on a Saturday or Sunday)

.. code-block:: python

    # 2011-01-01 is Saturday
    assert mondayise(year=2011, month=1, day=1,
                     cases=((WEEKDAY_SAT, WEEKDAY_MON),
                            (WEEKDAY_SUN, WEEKDAY_MON),)) == "2011-01-03"

2. Day after New Year's Day: 2 January (or the following Monday if it falls on a Saturday, or the following Tuesday if it falls on a Sunday)

.. code-block:: python

    # 2011-01-02 is Sunday
    assert mondayise(year=2011, month=1, day=2,
                     cases=((WEEKDAY_SAT, WEEKDAY_MON),
                            (WEEKDAY_SUN, WEEKDAY_TUE),)) == "2011-01-04"

``nth_weekday``
~~~~~~~~~~~~~~~
Labour Day: The fourth Monday in October

.. code-block:: python

    assert nth_weekday(year=2014, month=10, n=4, weekday=WEEKDAY_MON) == "2014-10-27"

``next_weekday``
~~~~~~~~~~~~~~~~
Marlborough provincial anniversary day: First Monday after Labour Day

.. code-block:: python

    assert next_weekday(year=2014, month=10, day=27, weekday=WEEKDAY_MON) == "2014-11-03"

``nearest_weekday``
~~~~~~~~~~~~~~~~~~~
Wellington provincial anniversary day: 22 January (Monday nearest to the actual day)

.. code-block:: python

    # 2014-01-22 is Wednesday
    assert nearest_weekday(year=2014, month=1, day=22, weekday=WEEKDAY_MON) == "2014-01-20"

``last_weekday``
~~~~~~~~~~~~~~~~
Memorial Day: Last Monday in May

.. code-block:: python

    assert last_weekday(year=2014, month=5, weekday=WEEKDAY_MON) == "2014-05-26"

``next_date``
~~~~~~~~~~~~~
Inauguration Day: First January 20 following a Presidential election

.. code-block:: python

    # 2012-11-06 was the previous presidential election day in US
    assert next_date(month=1, day=20, offset=(2012, 11, 6)) == "2013-01-20"

License
-------
All the code is licensed under the GNU Lesser General Public License (v3+).

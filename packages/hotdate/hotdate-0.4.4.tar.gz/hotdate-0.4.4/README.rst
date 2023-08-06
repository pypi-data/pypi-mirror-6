hotdate |Build Status|
======================

``hotdate`` is a library for doing friendly date formating. Its API is
inspired by `Moment.js <http://momentjs.com>`__.

``hotdate`` wraps Python's builtin ``datetime`` object with a layer that
simplifies some common operations that are annoying to do with
``datetime``. More importantly, ``hotdate`` provides functionality for
doing friendly/human-readable relative date formatting. It even has one
of those crazy "fluent interfaces" that are so hip with the kids these
days.

A quick tour
------------

Construction
~~~~~~~~~~~~

You can create hotdate objects in a bunch of ways.

.. code:: python

        from hotdate import hotdate

        # get the current time and date
        >>> hotdate()
        hotdate(2014, 3, 4, 21, 34, 3, 661600)

.. code:: python

        >>> hotdate(2011)
        hotdate(2011, 1, 1, 0, 0)

.. code:: python

        >>> hotdate('2012 03', '%Y %m')
        hotdate(2012, 3, 1, 0, 0)

.. code:: python

        >>> d = datetime.datetime.now()
        >>> hotdate(d)
        hotdate(2014, 3, 4, 21, 34, 3, 661600)

Formatting
~~~~~~~~~~

You can use it to format dates:

.. code:: python


        >>> hotdate().format()
        '2014-03-04T21:46:18'

.. code:: python

        
        >>> hotdate().format('%c')
        'Tue Mar  4 21:47:03 2014'

"How long ago?"
~~~~~~~~~~~~~~~

.. code:: python


        >>> hotdate().from_now()
        'just now'

.. code:: python

        >>> hotdate(2011).from_now()
        '2 years ago'

.. code:: python

        >>> hotdate().add(minutes=30).from_now()
        '29 minutes from now'

Calendar date formatting
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python


        >>> hotdate().calendar()
        'Today at 09:50PM'

.. code:: python

        >>> hotdate().add(days=1).calendar()
        'Tomorrow at 09:51PM'

.. code:: python

        >>> hotdate().subtract(days=4).calendar()
        'Last Friday at 09:51PM'

.. code:: python

        >>> hotdate(2011).calendar()
        '1/1/2011'

Use it just like a datetime
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

        >>> hotdate().isoformat()
        '2014-03-05T17:00:28.699772'

.. code:: python

        >>> hotdate.fromtimestamp(1311218002)
        hotdate(2011, 7, 20, 23, 13, 22)

.. code:: python

        >>> hotdate().timetuple()
        time.struct_time(tm_year=2014, tm_mon=3, tm_mday=5, tm_hour=17, tm_min=10, tm_sec=35, tm_wday=2, tm_yday=64, tm_isdst=-1)

.. |Build Status| image:: https://travis-ci.org/mansam/hotdate.png?branch=master
   :target: https://travis-ci.org/mansam/hotdate

# -*- coding: utf-8 -*-
"""
hotdate
An intuitive date processing library.

Author: Sam Lucidi <sam@samlucidi.com>

"""

from datetime import datetime, timedelta
from six import string_types
__version__ = "0.2.1"


class hotdate(datetime):
    """
    'hotdate' objects wrap datetime, providing
    all the familiar methods of that class
    as well as a set of methods for friendly
    formatting of dates.

    """

    _units = {
        'year': 3.15569e7,
        'month': 2.62974e6,
        'day': 86400,
        'hour': 3600,
        'minute': 60,
        'second': 1,
    }

    _property_ordering = [
        'year',
        'month',
        'day',
        'hour',
        'minute',
        'second',
        'microsecond'
    ]

    def __new__(cls, year=0, month=1, day=1, hour=0, minute=0,
                second=0, microsecond=0, tzinfo=None):
        """
        Create a new 'hotdate' object. There are a few different
        ways to call this that do different things:

        1. no params:
            Just calling hotdate() gets you a shiny new
            hotdate object representing the current moment.
            (i.e. datetime.datetime.now())

        2. date formating:
            If you pass two strings to hotdate(),
            the first argument is treated as a date string
            and the second argument is treated as a strftime
            format string.

            This lets you do things like 'hotdate("2014", "%Y")',
            which in this example would give you a hotdate object
            representing 1/1/2014 at 00:00:00.

        3. datetime conversion
            If you pass in a datetime object as hotdate's first
            argument, it will promote the datetime to a hotdate
            object.

        4. datetime-alike:
            You can also just pass in all the normal datetime parameters,
            starting with the year. Unlike datetime, hotdate will let you
            leave out everything but the year, so you can do something like
            'hotdate(2011)' and hotdate will set the other parameters to their
            minimum values. That example would give you a hotdate object
            representing 1/1/2011 at 00:00:00.

        """

        if isinstance(year, string_types) and isinstance(month, string_types):
            # some gnarly argument overloading here
            # so that we can do format strings as
            # positional args without breaking
            # the creation of datetimes.
            datestr = year
            fstr = month
            obj = hotdate.strptime(datestr, fstr)
        elif isinstance(year, datetime):
            # overloading to allow
            # converting a datetime into
            # a hotdate object.
            dt = year
            obj = hotdate.from_datetime(dt)
        elif year:
            obj = super(
                hotdate,
                cls).__new__(
                cls,
                year,
                month,
                day,
                hour,
                minute,
                second,
                microsecond,
                tzinfo)
        else:
            now = datetime.now()
            obj = hotdate.from_datetime(now)
        return obj

    def format(self, fstr=None, microseconds=False):
        """
        Format this hotdate object with the
        provided format string, or just
        iso8601 format it if none is
        provided.

        """

        if fstr:
            output = self.strftime(fstr)
        else:
            output = hotdate.isoformat(self)
            if not microseconds:
                output = output.split(".")[0]
        return output

    def from_now(self):
        """
        Return a human readable string
        that indicates the distance between
        this hotdate object and the current time.

        """

        now = hotdate.now()
        delta = self - now
        days = int(abs(delta.total_seconds() / 86400))
        seconds = int(abs(delta.total_seconds()))
        unit = ''
        units = 0
        # this is all very approximate
        if days / 365.0 >= 1:
            unit = "year"
            units = int(days / 365.0)
        elif days / 30.0 >= 1:
            unit = "month"
            units = int(days / 30.0)
        elif days / 7.0 >= 1:
            unit = "week"
            units = int(days / 7.0)
        elif days > 0:
            unit = "day"
            units = days
        elif seconds / 3600.0 >= 1:
            unit = "hour"
            units = int(seconds / 3600.0)
        elif seconds / 60.0 >= 1:
            unit = "minute"
            units = int(seconds / 60.0)
        else:
            unit = "second"
            units = seconds
        if delta.days < 0 or delta.seconds < 0:
            suffix = "ago"
        else:
            suffix = "from now"
        return hotdate._ago_string(unit, units, suffix)

    def add(self, **args):
        """
        Add the number of time units specified in
        the keyword args to this object, returning
        a new hotdate object.

        Valid kwargs are year, month, day, hour, minute, second.
        It's also acceptable to pluralize them for readability's
        sake, e.g. you can do either of these:
            hotdate().add(year=1, day=15)
            hotdate().add(years=1, days=15)

        """

        seconds = 0
        for k, v in args.items():
            if k.endswith('s'):
                k = k[:-1]
            seconds += (self._units[k] * v)

        d = self + timedelta(seconds=seconds)
        return hotdate.from_datetime(d)

    def subtract(self, **args):
        """
        Subtract the number of time units specified in
        the keyword args to this object, returning
        a new hotdate object.

        Valid kwargs are year, month, day, hour, minute, second.
        It's also acceptable to pluralize them for readability's
        sake, e.g. you can do either of these:
            hotdate().subtract(year=1, day=15)
            hotdate().subtract(years=1, days=15)

        """

        seconds = 0
        for k, v in args.items():
            if k.endswith('s'):
                k = k[:-1]
            seconds += (self._units[k] * v)

        d = self - timedelta(seconds=seconds)
        return hotdate.from_datetime(d)

    def calendar(self):
        """
        Return a string that would be
        suitable for display in something
        like a calendar or reminder app.
        The exact format to be returned
        depends on the distance between
        the object this is called on and
        the current date.

        In the event of a long distance,
        it returns the locale's date
        format, e.g. 1/1/2014.

        For closer dates, it will return
        strings along the lines of:
            "Yesterday at 2:31pm"
            "Tomorrow at 4:01am"
            "Last Thursday at 9:00am"

        """

        today = when.now()

        delta = today - self
        prefix = ''
        calday = ''
        use_calday = False
        # TODO: refactor this godawful mess when
        # I am actually awake
        if -7 < delta.days < 0:
            use_calday = True
        if 7 > delta.days > 0:
            prefix = 'Last '
            use_calday = True
        if delta.days == 0:
            use_calday = True
        if use_calday:
            if today.day == (self.day - 1):
                calday = 'Tomorrow'
            elif today.day == (self.day + 1):
                calday = 'Yesterday'
                prefix = ''
            elif today.day == self.day:
                calday = 'Today'
            else:
                calday = self.strftime('%A')
            return '{}{} at {}'.format(
                prefix, calday, self.strftime('%I:%M%p'))
        else:
            return self.strftime('%x')

    def start_of(self, unit):
        """
        Return a hotdate object representing
        the beginning of the chosen time unit.

        For example, hotdate(2014).start_of('year')
        would return a hotdate representing the
        date 1/1/2014 at 00:00:00

        """

        props = {}
        ix = self._property_ordering.index(unit)
        for prop in self._property_ordering:
            props[prop] = getattr(self, prop)
            if self._property_ordering.index(prop) > ix:
                if prop in ['month', 'day']:
                    props[prop] = 1
                else:
                    props[prop] = 0
        return hotdate(**props)

    def end_of(self, unit):
        """
        Return a hotdate object representing
        the end of the chosen time unit.

        For example, hotdate(2014).end_of('year')
        would return a hotdate representing the
        date 12/31/2014 at 23:59:59

        """

        props = {}
        ix = self._property_ordering.index(unit)
        for prop in self._property_ordering[:(ix + 1)]:
            props[prop] = getattr(self, prop)
            if prop == unit:
                props[prop] += 1
        return hotdate.from_datetime(hotdate(**props) - timedelta(seconds=1))

    @classmethod
    def from_datetime(cls, dt):
        """
        Promote a datetime to
        a hotdate object.

        """

        h = hotdate(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            dt.tzinfo)
        return h

    @classmethod
    def _ago_string(cls, unit, units, suffix):
        """
        Produce a nicely formatted timeago string.

        """

        if units == 0:
            return "just now"
        else:
            article = 'a'
            if unit == 'hour':
                article = article + 'n'
            if units == 1:
                units = article
            else:
                unit = unit + 's'
            return "{} {} {}".format(units, unit, suffix)

"""Data types"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from datetime import datetime as _datetime

import spruce.datetime as _dt
import sqlalchemy.types as _sqla_types


class DateTimeWithTimeZone(_sqla_types.TypeDecorator):

    """A date-time interpreted as being in a particular time zone

    Some databases do not natively support time-zone-aware date-times.
    Others support them but have this feature misconfigured or misused.  In
    either case, it is necessary to override the time zone on values
    returned from the database.  This data type performs such an override
    automatically.

    :param tz:
        The time zone that should be applied to the values handled by this
        type.
    :type tz: :class:`datetime.tzinfo`

    """

    def __init__(self, tz):
        super(DateTimeWithTimeZone, self).__init__()
        self._timezone = tz

    impl = _sqla_types.DateTime

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.replace(tzinfo=self.timezone)
        else:
            return value

    @property
    def python_type(self):
        return _datetime

    @property
    def timezone(self):
        return self._timezone


class UnixTime(_sqla_types.TypeDecorator):

    """A Unix time

    A Unix time is an integer representation of a date-time.  This data type
    provides a time-zone-aware :class:`~datetime.datetime` interface for
    each underlying Unix time value.

    :param tz:
        The time zone to which fetched values should be converted.  If null,
        then they will remain in UTC.
    :type tz: :class:`datetime.tzinfo` or null

    """

    def __init__(self, tz=None):
        super(UnixTime, self).__init__()
        self._timezone = tz

    impl = _sqla_types.Integer

    def process_bind_param(self, value, dialect):
        if value is not None:
            return _dt.unixtime_from_datetime(value)
        else:
            return value

    def process_result_value(self, value, dialect):
        if value is not None:
            dt = _dt.datetime_from_unixtime(value)
            if self.timezone:
                dt = dt.astimezone(self.timezone)
            return dt
        else:
            return value

    @property
    def python_type(self):
        return _datetime

    @property
    def timezone(self):
        return self._timezone

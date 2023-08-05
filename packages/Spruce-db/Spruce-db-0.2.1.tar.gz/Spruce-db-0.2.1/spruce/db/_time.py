"""Dates and times"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from spruce.datetime \
    import datetime_from_unixtime as _datetime_from_unixtime, \
           localtime_datetime_from_unixtime \
               as _localtime_datetime_from_unixtime
import sqlalchemy as _sqla


def current_datetime(engine):
# TODO (Python 3):
#def current_datetime(*, engine):
    """The current date and time on the database server

    The result is a time zone aware :class:`datetime.datetime` in UTC.

    :param engine:
        A database interaction engine.
    :type engine: :class:`sqlalchemy.engine.base.Engine`

    :rtype: :class:`datetime.datetime`

    """
    return _datetime_from_unixtime(current_unixtime(engine=engine))


def current_localtime_datetime(engine):
# TODO (Python 3):
#def current_localtime_datetime(*, engine):
    """The current date and time on the database server, in local time

    The result is a time zone aware :class:`datetime.datetime` in local
    time.

    :param engine:
        A database interaction engine.
    :type engine: :class:`sqlalchemy.engine.base.Engine`

    :rtype: :class:`datetime.datetime`

    """
    return _localtime_datetime_from_unixtime(current_unixtime(engine=engine))


def current_naive_datetime(engine):
# TODO (Python 3):
#def current_naive_datetime(*, engine):
    """The current date and time on the database server

    The result is a naive :class:`datetime.datetime` in the time zone used
    by the database server.

    :param engine:
        A database interaction engine.
    :type engine: :class:`sqlalchemy.engine.base.Engine`

    :rtype: :class:`datetime.datetime`

    """
    return engine.execute(current_timestamp_deferred(engine=engine)).scalar()


def current_timestamp_deferred(engine=None):
# TODO (Python 3):
#def current_timestamp_deferred(*, engine=None):
    """The current time on the database server

    This is a database abstraction layer object that evaluates to
    ``CURRENT_TIMESTAMP`` (or equivalent) on flush.  If executed by a
    database engine, the result is a naive :class:`datetime.datetime` in the
    timezone used by the database server.

    :param engine:
        A database interaction engine.
    :type engine: :class:`sqlalchemy.engine.base.Engine` or null

    :rtype: :class:`sqlalchemy.sql.functions.current_timestamp`

    """
    return _sqla.func.current_timestamp(engine=engine)


def current_unixtime(engine):
# TODO (Python 3):
#def current_unixtime(*, engine):
    """The current time on the database server

    :param engine:
        A database interaction engine.
    :type engine: :class:`sqlalchemy.engine.base.Engine`

    :rtype: :class:`int`

    """
    return engine.execute(current_unixtime_deferred(engine=engine)).scalar()


def current_unixtime_deferred(engine=None):
# TODO (Python 3):
#def current_unixtime_deferred(*, engine=None):
    """The current Unix time on the database server

    This is a database abstraction layer object that evaluates to
    ``UNIX_TIMESTAMP(CURRENT_TIMESTAMP)`` (or equivalent) on flush.

    :param engine:
        A database interaction engine.
    :type engine: :class:`sqlalchemy.engine.base.Engine` or null

    :rtype: :class:`sqlalchemy.sql.expression.Function`

    """
    return _sqla.func.unix_timestamp(engine=engine)

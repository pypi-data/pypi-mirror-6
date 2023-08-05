"""Interaction engines"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import sqlalchemy as _sqla

from . import _connparams


def engine_from_connparams(connparams, *create_engine_args,
                           **create_engine_kwargs):
    """An interaction engine derived from connection parameters

    :param connparams:
        Connection parameters.
    :type connparams: :class:`~spruce.db._connparams.connparams`

    :param create_engine_args:
        Additional arguments that are passed to
        :func:`sqlalchemy.create_engine`.

    :param create_engine_kwargs:
        Additional arguments that are passed to
        :func:`sqlalchemy.create_engine`.

    :rtype: :class:`sqlalchemy.engine.base.Engine`

    :raise spruce.db.InsufficientConnSettings:
        Raised if the given *connparams* are insufficient to attempt a
        connection.

    .. seealso:: :func:`engine_from_settings`, :func:`std_engine`

    """
    connparams.require_valid()
    return _sqla.create_engine(unicode(connparams), *create_engine_args,
                               **create_engine_kwargs)


def engine_from_settings(settings,
                         group=None,
                         dialect_key='dialect',
                         driver_key='driver',
                         server_key='server',
                         port_key='port',
                         user_key='user',
                         password_key='password',
                         db_key='db',
                         other_params_keys=None,
                         *create_engine_args,
                         **create_engine_kwargs):

    """A interaction engine derived from application settings

    .. note::
        This is a convenience function that uses \
        :func:`~spruce.db._connparams.connparams_from_settings` and \
        :func:`engine_from_connparams`.

    :param settings:
        Application settings open for reading.
    :type settings:
        :class:`spruce.settings.Settings <spruce.settings._core.Settings>`

    :param group:
        The name of a settings group within the the given *settings*
        object's current group.
    :type group: :obj:`str` or null

    :param str dialect_key:
        The persistent settings key whose value is the SQL dialect name.

    :param str driver_key:
        The persistent settings key whose value is the SQL driver name.

    :param str server_key:
        The persistent settings key whose value is the server's IP address
        or DNS name.

    :param str port_key:
        The persistent settings key whose value is the port number.

    :param str user_key:
        The persistent settings key whose value is the user name.

    :param str password_key:
        The persistent settings key whose value is the password.

    :param str db_key:
        The persistent settings key whose value is the database name.

    :param other_params_keys:
        Persistent settings keys of additional parameters that are passed to
        the SQL driver when establishing a connection.
    :type other_params_keys: [:obj:`str`] or null

    :param create_engine_args:
        Additional arguments that are passed to
        :func:`sqlalchemy.create_engine`.

    :param create_engine_kwargs:
        Additional arguments that are passed to
        :func:`sqlalchemy.create_engine`.

    :rtype: :class:`sqlalchemy.engine.base.Engine`

    :raise spruce.settings.MissingRequiredSettingsValue:
        Raised if *dialect_key* is missing in the given *group* of
        *settings*.

    .. seealso:: :func:`std_engine`

    """

    connparams = _connparams.connparams_from_settings\
                  (settings,
                   group,
                   dialect_key=dialect_key,
                   driver_key=driver_key,
                   server_key=server_key,
                   port_key=port_key,
                   user_key=user_key,
                   password_key=password_key,
                   db_key=db_key,
                   other_params_keys=other_params_keys,
                   required=True)
    return engine_from_connparams(connparams, *create_engine_args,
                                  **create_engine_kwargs)


def std_engine(name, settings, dialect=None, driver=None, server=None,
               port=None, user=None, password=None, db=None, other_params=None,
               *create_engine_args, **create_engine_kwargs):

    """An interaction engine from standard settings

    The engine is set up using the connection parameters from standard
    settings for the connection with the given *name*.  See
    :func:`std_connparams() <spruce.db._connparams.std_connparams>` for
    an explanation of how these are determined.

    :param str name:
        The name of a database connection in standard settings.

    :param settings:
        Application settings open for reading.
    :type settings:
        :class:`spruce.settings.Settings <spruce.settings._core.Settings>`

    :param dialect:
        The SQL dialect name.
    :type dialect: :obj:`str` or null

    :param driver:
        The SQL driver name.
    :type driver: :obj:`str` or null

    :param server:
        The server's IP address or DNS name.
    :type server: :obj:`str` or null

    :param port:
        The port number.
    :type port: int or :obj:`str` or null

    :param user:
        The username.
    :type user: :obj:`str` or null

    :param password:
        The password.
    :type password: :obj:`str` or null

    :param db:
        The database name.
    :type db: :obj:`str` or null

    :param other_params:
        Additional parameters that are passed to the SQL driver when
        establishing a connection.
    :type other_params: {:obj:`object`: :obj:`object`}

    :param create_engine_args:
        Additional arguments that are passed to
        :func:`sqlalchemy.create_engine`.

    :param create_engine_kwargs:
        Additional arguments that are passed to
        :func:`sqlalchemy.create_engine`.

    :rtype: :class:`sqlalchemy.engine.base.Engine`

    :raise spruce.settings.MissingRequiredSettingsValue:
        Raised if *dialect* is null and ``dialect`` is missing in both the
        ``dbconn/__default__`` and the :samp:`dbconn/{name}` groups of
        *settings*.

    .. seealso::
        :func:`engine_from_connparams`, :func:`engine_from_settings`

    """

    other_params = other_params if other_params is not None else {}

    # NOTE: even though the parameters passed in to this function are used as
    #   overrides below, we set them as defaults here so that we can take
    #   advantage of ``std_connparams(..., required_in_settings=True, ...)``
    with settings.ingroup('dbconn/{}'.format(name)):
        for name_ in ('dialect', 'driver', 'server', 'port', 'user',
                      'password', 'db', 'other_params'):
            value = locals()[name_]
            if value is not None:
                settings.defaults[settings.absname(name_)] = value

    connparams = _connparams.std_connparams(name,
                                            settings=settings,
                                            dialect=dialect,
                                            driver=driver,
                                            server=server,
                                            port=port,
                                            user=user,
                                            password=password,
                                            db=db,
                                            required_in_settings=True,
                                            **other_params)
    return engine_from_connparams(connparams, *create_engine_args,
                                  **create_engine_kwargs)

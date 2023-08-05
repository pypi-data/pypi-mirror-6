"""Connection parameters"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from urllib import quote as _percent_encoded, urlencode as _urlencoded

from spruce.collections import odict as _odict
from spruce.lang import converter as _converter, pos_int as _pos_int
import spruce.settings as _settings

from . import _exc


def connparams_from_settings(settings,
                             group=None,
                             dialect_key='dialect',
                             driver_key='driver',
                             server_key='server',
                             port_key='port',
                             user_key='user',
                             password_key='password',
                             db_key='db',
                             other_params_keys=None,
                             required=False):

    """Database connection parameters derived from persistent settings

    The given *\*_key* parameters are used to look up the values of the
    database connection parameters.  The keys are resolved relative to the
    given *group* (if any) within the given *settings* object's
    :attr:`current group <spruce.settings._core.Settings.group>`.

    :param settings:
        Application settings open for reading.
    :type settings:
        :class:`spruce.settings.Settings <spruce.settings._core.Settings>`

    :param group:
        The name of the settings group (within the given *settings* object's
        current group) that contains the settings.
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

    :param bool required:
        Whether a valid set of connection parameters is required to be
        defined in the specified persistent settings.

    :rtype: :class:`connparams`

    :raise spruce.settings.MissingRequiredSettingsValue:
        Raised if *required* is true and *dialect_key* is missing in the
        given *group* of *settings*.

    .. seealso:: :func:`connparams`

    """

    with settings.ingroup(group):
        dialect = settings.value(dialect_key, required=required)
        driver = settings.value(driver_key)
        server = settings.value(server_key)
        port = settings.intvalue(port_key)
        user = settings.value(user_key)
        password = settings.value(password_key)
        db = settings.value(db_key)
        other_params = {}
        if other_params_keys:
            for key in other_params_keys:
                other_params[key] = settings.value(key)

    return connparams(dialect=dialect, driver=driver, server=server, port=port,
                      user=user, password=password, db=db, **other_params)


def std_connparams(name, settings, dialect=None, driver=None, server=None,
                   port=None, user=None, password=None, db=None,
                   required_in_settings=False, **other_params):

    """Database connection parameters derived from standard settings

    The parameters are constructed as follows:

      #. The parameters are read from persistent settings in the
         ``dbconn/__default__`` group if they exist there.

      #. The parameters are read from persistent settings in the
         :samp:`dbconn/{name}` group if they exist there.  These override
         any previously acquired corresponding parameters.

      #. Any parameters that are provided as arguments to this function are
         applied so that they override any previously acquired corresponding
         parameters.

    :param str name:
        The name of a database connection in standard settings.

    :param bool required_in_settings:
        Whether a valid database connection is required to be found in
        standard settings, not including the specific overriding parameters
        passed in to this function.

    :rtype: :class:`connparams`

    :raise spruce.settings.MissingRequiredSettingsValue:
        Raised if *required_in_settings* is true and *dialect_key* is
        missing in both the ``dbconn/__default__`` and the
        :samp:`dbconn/{name}` groups of *settings*.

    .. seealso:: :func:`connparams_from_settings`, :class:`connparams`

    """

    with settings.ingroup('dbconn'):
        default_connparams = connparams_from_settings(settings, '__default__')

        with settings.ingroup(name):
            if default_connparams:
                for name_ in ('dialect', 'driver', 'server', 'port', 'user',
                              'password', 'db', 'other_params'):
                    value = getattr(default_connparams, name_)
                    if value is not None:
                        settings.defaults[settings.absname(name_)] = value

            connparams_ = \
                connparams_from_settings(settings,
                                         required=required_in_settings)

    args_connparams = connparams(dialect=dialect, driver=driver, server=server,
                                 port=port, user=user, password=password,
                                 db=db, **other_params)
    connparams_.update(args_connparams)

    return connparams_


class connparams(object):

    """Database connection parameters

    The :obj:`str` representation of a :class:`!connparams` object is a
    database URI, also known as a database source name (DSN).

    :param dialect:
        The SQL dialect name.
    :type dialect: :obj:`str` or null

    :param driver:
        The SQL driver name.
    :type driver: :obj:`str` or null

    :param server:
        The IP address or DNS name.
    :type server: :obj:`str` or null

    :param port:
        The port number.
    :type port: ~\ :obj:`int` or null

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

    :raise TypeError:
        Raised if a non-null *port* is given that is of a type that cannot
        be converted to an :obj:`int`.

    :raise ValueError:
        Raised if

          * *dialect* is an empty string or

          * a non-null *port* is given that cannot be converted to an
            :obj:`int`.

    """

    def __init__(self, dialect=None, driver=None, server=None, port=None,
                 user=None, password=None, db=None, **other_params):

        self.dialect = dialect
        self.driver = driver
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self._other_params = other_params.copy()

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               ', '.join('{}={!r}'.format(property_, value)
                                         for property_, value
                                         in self._init_args(ordered=True)
                                                .items()
                                         if value is not None))

    def __str__(self):

        if not self.dialect:
            return ''

        string = self.dialect
        if self.driver:
            string += '+' + self.driver
        string += '://'

        if self.server:
            if self.user:
                string += _percent_encoded(self.user)
                if self.password:
                    string += ':' + _percent_encoded(self.password)
                string += '@'
            string += _percent_encoded(self.server)
            if self.port is not None:
                string += ':' + str(self.port)

        if self.db:
            string += '/' + _percent_encoded(self.db)

        if self.other_params:
            string += '?' + _urlencoded(self.other_params)

        return string

    def copy(self):
        return self.__class__(**self._init_args())

    @property
    def db(self):
        """The database name

        :type: :obj:`str` or null

        """
        return self._db

    @db.setter
    def db(self, value):
        if value is not None:
            db = unicode(value)
            self._db = db
        else:
            self._db = None

    @property
    def dialect(self):
        """The SQL dialect name

        :type: :obj:`str` or null

        :raise ValueError:
            Raised if an empty string is assigned.

        """
        return self._dialect

    @dialect.setter
    def dialect(self, value):
        if value is not None:
            dialect = unicode(value)
            if not dialect:
                raise ValueError('invalid dialect {!r}: expecting a non-empty'
                                  ' string')
            self._dialect = dialect
        else:
            self._dialect = None

    @property
    def driver(self):
        """The SQL driver name

        :type: :obj:`str` or null

        """
        return self._driver

    @driver.setter
    def driver(self, value):
        if value is not None:
            driver = unicode(value)
            self._driver = driver
        else:
            self._driver = None

    @property
    def other_params(self):
        """
        Additional parameters that are passed to the SQL driver when
        establishing a connection

        :type: {:obj:`str`: :obj:`object`}

        """
        return self._other_params

    @property
    def password(self):
        """The password

        :type: :obj:`str` or null

        """
        return self._password

    @password.setter
    def password(self, value):
        if value is not None:
            password = unicode(value)
            self._password = password
        else:
            self._password = None

    @property
    def port(self):
        """The port number used to connect to the database server

        :type: ~\ :obj:`int` or null

        :raise TypeError:
            Raised if a non-null value is assigned that is of a type that
            cannot be converted to an :obj:`int`.

        :raise ValueError:
            Raised if a non-null value is assigned that cannot be converted to
            an :obj:`int`.

        """
        return self._port

    @port.setter
    def port(self, value):
        if value is not None:
            port = _port(value)
            self._port = port
        else:
            self._port = None

    def require_valid(self):
        """
        Require that these connection parameters contain enough information to
        attempt a connection

        :raise spruce.db.InsufficientConnSettings:
            Raised if :attr:`valid` is false.

        .. seealso:: :attr:`valid`

        """
        if not self.valid:
            missing_attrs = [attrname for attrname in ('dialect',)
                             if getattr(self, attrname) is None]
            raise _exc.InsufficientConnSettings(missing_attrs=missing_attrs)

    @property
    def server(self):
        """The address of the database server

        This is an IP address or DNS name.

        :type: :obj:`str` or null

        .. note:: **TODO:**
            raise :exc:`ValueError` if a non-null value is assigned that is
            neither an IP address nor a DNS name

        """
        return self._server

    @server.setter
    def server(self, server):
        # FIXME: validate
        self._server = server

    def update(self, other):
        """Update these connection parameters with values from some others

        This causes any non-null values assigned to the *other* parameters'
        properties to replace the corresponding values of these ones.
        :attr:`other_params` is updated using :meth:`dict.update`.

        :param other:
            The other connection parameters.
        :type other: :class:`connparams`

        """
        if other.dialect is not None:
            self.dialect = other.dialect
        if other.driver is not None:
            self.driver = other.driver
        if other.server is not None:
            self.server = other.server
        if other.port is not None:
            self.port = other.port
        if other.user is not None:
            self.user = other.user
        if other.password is not None:
            self.password = other.password
        if other.db is not None:
            self.db = other.db
        self._other_params.update(other.other_params)

    @property
    def user(self):
        """The username

        :type: :obj:`str` or null

        """
        return self._user

    @user.setter
    def user(self, user):
        self._user = user

    @property
    def valid(self):
        """
        Whether these connection parameters contain enough information to
        attempt a connection

        :type: :obj:`bool`

        .. seealso:: :meth:`require_valid`

        """
        return self.dialect is not None

    def _init_args(self, ordered=False):
        class_ = _odict if ordered else dict
        args = class_((('dialect', self.dialect),
                       ('driver', self.driver),
                       ('server', self.server),
                       ('port', self.port),
                       ('user', self.user),
                       ('password', self.password),
                       ('db', self.db)))
        args.update(self.other_params)


@_converter('port', _pos_int.annotated_totype.displayname())
def _port(value):
    return _pos_int(value)

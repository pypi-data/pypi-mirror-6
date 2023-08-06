"""Hybrid properties

.. seealso:: :mod:`sqlalchemy.ext.hybrid`

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from sqlalchemy.ext.hybrid import hybrid_property as _sqla_hybrid_property


def hybridized_property(property):

    """A non-ORM underlying class property cast as a hybrid ORM property

    This function is useful when an ORM class extends some underlying
    non-ORM class with ORM behavior and it is desirable to retain the
    behavior of some underlying property while making it available as a
    hybrid attribute in ORM queries.

    To use it, for each property in the underlying non-ORM class, apply this
    pattern in the ORM class:

      #. For each of the property's underlying private attributes (typically
         there's just one) that corresponds to a column in the ORM class's
         table, override that attribute with the appropriate ORM column
         declaration.

      #. Override the property with the result of calling this function on
         the property (referenced as an attribute of the non-ORM class).

    For example, suppose there is a :class:`!User` class defined like so::

        class User(object):

            def __init__(self, name, domain):
                self._domain = domain
                self._name = name

            @property
            def address(self):
                return '{}@{}'.format(self.name, self.domain)

            @address.setter
            def address(self, value):
                name, domain = value.split('@', 1)
                self.name = name
                self.domain = domain

            @property
            def domain(self):
                return self._domain

            @domain.setter
            def domain(self, value):
                self._domain = domain

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, value):
                self._name = name

    Suppose that we subsequently want to extend this class with ORM
    semantics, leaving the current class as is to avoid introducing
    needless dependencies.  For the sake of argument, call the new class
    :class:`!OrmUser`.  Suppose that the corresponding database table only
    has the columns ``name`` and ``domain``.  When implementing
    :class:`!OrmUser`, we could ordinarily deal with :class:`!User`\ 's
    properties in one of several ways:

      :attr:`!domain` and :attr:`!name`

        * Replace them with ORM attributes.

          * Disadvantage: code duplication.  If we later add (for example)
            validation to :class:`!User`\ 's propreties, then we need to
            carefully duplicate it in :class:`!OrmUser`.

        * Leave them as they are, instead replacing :attr:`!_domain` and
          :attr:`!_name` with ORM-mapped attributes.

          * Disadvantage: not usable in ORM queries.

      :attr:`!address`

        * Leave it as it is.

          * Disadvantage: not usable in ORM queries.

        * Reimplement it as an hybrid ORM property.

          * Disadvantage: code duplication.

    This function provides an alternative that avoids the disadvantages of
    these approaches.  Suppose that the schema of :class:`!OrmUser`\ 's
    underlying table is already defined as ``users_table``.  Define
    :class:`!OrmUser` like so::

        import sqlalchemy.orm as _sqla_orm

        OrmObject = _sqla_orm.declarative_base()

        class OrmUser(OrmObject, User):

            __table__ = users_table

            address = hybridized_property(User.address)

            @address.expression
            def address(self):
                return _sqla_func.concat(self.name, '@', self.domain)

            domain = hybridized_property(User.domain)

            name = hybridized_property(User.name)

            _domain = users_table.c.domain

            _name = users_table.c.name

    The result duplicates none of the original code and can be used for ORM
    queries such as ::

        alice = session.query(OrmUser)\\
                       .filter_by(address='alice@example.net')\\
                       .one()

    """

    if property.fget:
        def new_fget(self):
            return property.fget(self)
        new_fget.func_name = property.fget.func_name
    else:
        new_fget = None

    if property.fset:
        def new_fset(self, value):
            return property.fset(self, value)
        new_fset.func_name = property.fset.func_name
    else:
        new_fset = None

    if property.fdel:
        def new_fdel(self):
            return property.fdel(self)
        new_fdel.func_name = property.fdel.func_name
    else:
        new_fdel = None

    return _sqla_hybrid_property(new_fget, new_fset, new_fdel)

"""Exceptions"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import exceptions as _py_exc


class Exception(_py_exc.Exception):
    pass


class Error(RuntimeError, Exception):
    pass


class InsufficientConnSettings(Error):
    """The connection settings are insufficient

    :param missing_attrs:
        The required attributes that are missing.
    :type missing_attrs: ~[:obj:`str`]

    """
    def __init__(self, missing_attrs, message=None, *args):
        super(InsufficientConnSettings, self).__init__(missing_attrs, message,
                                                       *args)
        self._message = message
        self._missing_attrs = missing_attrs

    def __str__(self):
        message = 'insufficient connection settings'
        if self.missing_attrs:
            message += u' (missing attributes {})'.format(self.missing_attrs)
        if self.message:
            message += u': {}'.format(self.message)
        return message

    @property
    def message(self):
        return self._message

    @property
    def missing_attrs(self):
        return self._missing_attrs

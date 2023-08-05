"""
polaris.exc
~~~~~~~~~~~

:copyright: (c) 2013 Eleme, http://polaris.eleme.io
:license: MIT
"""


class PolarisError(Exception):
    """Generic error class."""


class ArguementError(PolarisError):
    """Raised when an invalid or conflicting function argument is supplied."""


class InvalidValueError(PolarisError):
    """Raised when an invalid argument value is supplied."""

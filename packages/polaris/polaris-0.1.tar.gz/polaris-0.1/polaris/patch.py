"""
    polaris.patch
    ~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    Inherit and patch 3rd party classes to make customized adjustment.
"""

__all__ = ["monkey_patch", "patch_sqlalchemy"]

import json
import uuid


def monkey_patch():
    patch_sqlalchemy()


def patch_sqlalchemy():
    import sqlalchemy
    sqlalchemy.UUID = UUID
    sqlalchemy.__all__.append('UUID')
    sqlalchemy.JSON = JSON
    sqlalchemy.__all__.append('JSON')


from sqlalchemy.dialects.postgresql import UUID as _UUID
from sqlalchemy.dialects.postgresql import JSON as _JSON
from sqlalchemy.types import TypeDecorator, VARCHAR


class UUID(TypeDecorator):
    """Platform-independent UUID type.

    Uses Postgresql's UUID type, otherwise uses VARCHAR(32), storing as
    stringified hex values.
    """
    impl = VARCHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(VARCHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        if dialect.name == 'postgresql':
            return value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        if dialect.name == 'postgresql':
            return value
        else:
            return uuid.UUID(value)


class JSON(TypeDecorator):
    """Platform-independent JSON type.

    Uses Postgresql's JSON type, otherwise uses VARCHAR, storing as json str.
    """

    impl = VARCHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(_JSON())
        else:
            return dialect.type_descriptor(VARCHAR())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        if dialect.name == 'postgresql':
            return value
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        if dialect.name == 'postgresql':
            return value
        else:
            return json.loads(value)

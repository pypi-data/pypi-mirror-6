from __future__ import absolute_import
import json
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import VARCHAR
from sqlalchemy.dialects import postgresql

try:
    postgresql.JSON
except AttributeError:
    raise NotImplementedError('This requires SQLAlchemy 0.9 or later')

class JSON(TypeDecorator):
    """Platform-independent JSON type.

    When using a PostgreSQL backend the native JSON type is used. On
    other databases values are stored as JSON-encoded string.

    Please note that this does not support any of the operators available
    for the `PostgreSQL JSON type
    <http://docs.sqlalchemy.org/en/rel_0_9/dialects/postgresql.html#sqlalchemy.dialects.postgresql.JSON>`_
    on other dialects.
    """

    impl = postgresql.JSON

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return self.impl
        else:
            return dialect.type_descriptor(VARCHAR)

    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        else:
            if value is not None:
                value = json.dumps(value)
            return value

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        else:
            if value is not None:
                value = json.loads(value)
            return value

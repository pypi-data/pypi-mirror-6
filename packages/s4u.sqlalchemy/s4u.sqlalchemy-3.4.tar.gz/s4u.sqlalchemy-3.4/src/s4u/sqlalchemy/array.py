import json
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import VARCHAR
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.mutable import Mutable


def _wl(func):
    def wrapper(self, *a, **kw):
        r = func(self, *a, **kw)
        self.changed()
        return r
    wrapper.__doc__ = wrapper.__doc__
    return wrapper


class MutableList(Mutable, list):
    __setitem__ = _wl(list.__setitem__)
    __detitem__ = _wl(list.__setitem__)
    __setslice__ = _wl(list.__setslice__)
    __detslice__ = _wl(list.__setslice__)
    append = _wl(list.append)
    extend = _wl(list.extend)
    insert = _wl(list.insert)
    pop = _wl(list.pop)
    reverse = _wl(list.reverse)
    sort = _wl(list.sort)

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __getstate__(self):
        return list(self)

    def __setstate__(self, state):
        list.__setitem__(self, slice(len(self)), state)


class Array(TypeDecorator):
    """Platform-independent mapping type.

    When using a PostgreSQL backend the native ARRAY type is used. On
    other databases values are stored as JSON-encoded string.

    Please note that this does not support any of the operators available
    for the `PostgreSQL ARRAY type
    <http://docs.sqlalchemy.org/en/rel_0_9/dialects/postgresql.html#sqlalchemy.dialects.postgresql.ARRAY`_
    on other dialects.
    """

    impl = postgresql.ARRAY

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
                if not isinstance(value, list):
                    raise ValueError('Value must be a list.')
                value = json.dumps(value)
            return value

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        else:
            if value is not None:
                value = json.loads(value)
            return value

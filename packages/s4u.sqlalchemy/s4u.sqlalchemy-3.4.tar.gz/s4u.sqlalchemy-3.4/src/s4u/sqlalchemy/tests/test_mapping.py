# vi: fileencoding=utf-8
import unittest
from ..testing import DatabaseTestCase
from ..testing import RoundTripTestCase


class MappingTests(unittest.TestCase):
    def Mapping(self, *a, **kw):
        from s4u.sqlalchemy.mapping import Mapping
        return Mapping(*a, **kw)

    def test_load_dialect_impl_postgresql(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        from sqlalchemy.dialects.postgresql import HSTORE
        mapping = self.Mapping()
        impl = mapping.load_dialect_impl(dialect())
        self.assertTrue(isinstance(impl, HSTORE))

    def test_load_dialect_impl_sqlite(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        from sqlalchemy.types import VARCHAR
        mapping = self.Mapping()
        impl = mapping.load_dialect_impl(dialect())
        self.assertTrue(isinstance(impl, VARCHAR))

    def test_process_bind_param_postgresql_passthrough(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        mapping = self.Mapping()
        input = object()
        output = mapping.process_bind_param(input, dialect())
        self.assertTrue(output is input)

    def test_process_bind_param_other_dialect_none(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        mapping = self.Mapping()
        self.assertEqual(mapping.process_bind_param(None, dialect()), None)

    def test_process_bind_param_other_dialect_with_data(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        mapping = self.Mapping()
        input = {u'foo': u'bâz'}
        output = mapping.process_bind_param(input, dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, '{"foo": "b\\u00e2z"}')

    def test_process_result_postgresql_passthrough(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        mapping = self.Mapping()
        input = object()
        output = mapping.process_result_value(input, dialect())
        self.assertTrue(output is input)

    def test_process_result_value_other_dialect_none(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        mapping = self.Mapping()
        self.assertEqual(mapping.process_result_value(None, dialect()), None)

    def test_process_result_value_other_dialect_with_data(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        mapping = self.Mapping()
        input = '{"foo": "b\\u00e2z"}'
        output = mapping.process_result_value(input, dialect())
        self.assertEqual(output, {u'foo': u'bâz'})


class MapRoundtrip(RoundTripTestCase):
    @classmethod
    def setupClass(cls):
        from sqlalchemy import schema
        from sqlalchemy import types
        from sqlalchemy.ext.mutable import MutableDict
        from s4u.sqlalchemy.mapping import Mapping
        super(MapRoundtrip, cls).setupClass()

        class Frop(cls.BaseObject):
            __tablename__ = 'frop'
            id = schema.Column(types.Integer(), primary_key=True)
            storage = schema.Column(MutableDict.as_mutable(Mapping), default=dict)

        cls.Frop = Frop
        cls.metadata.create_all()

    def test_roundtrip(self):
        obj = self.Frop()
        obj.id = 1
        obj.storage = {'1': 'One', '2': 'Two'}
        self.session.add(obj)
        self.session.flush()
        self.session.expire(obj)
        new = self.session.query(self.Frop).get(1)
        self.assertEqual(new.storage, {'1': u'One', '2': 'Two'})

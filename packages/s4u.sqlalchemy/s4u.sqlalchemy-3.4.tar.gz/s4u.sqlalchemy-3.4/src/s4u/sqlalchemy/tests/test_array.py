# vi: fileencoding=utf-8
import pickle
import unittest
from sqlalchemy import schema
from sqlalchemy import types
from ..array import Array
from ..array import MutableList
from ..testing import RoundTripTestCase


class MutableListTests(unittest.TestCase):
    def test_coerce_convert_list(self):
        lst = [1, 2, 3, 4]
        coerced = MutableList.coerce(None, lst)
        self.assertEqual(coerced, lst)
        self.assertTrue(isinstance(coerced, MutableList))

    def test_coerce_already_mutable(self):
        lst = MutableList([1, 2, 3, 4])
        self.assertTrue(MutableList.coerce(None, lst) is lst)

    def test_pickle(self):
        lst = MutableList([1, 2, 3, 4])
        self.assertEqual(lst, pickle.loads(pickle.dumps(lst)))


class ArrayTests(unittest.TestCase):
    def test_load_dialect_impl_postgresql(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        from sqlalchemy.dialects.postgresql import ARRAY
        array = Array(int)
        impl = array.load_dialect_impl(dialect())
        self.assertTrue(isinstance(impl, ARRAY))

    def test_load_dialect_impl_sqlite(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        from sqlalchemy.types import VARCHAR
        array = Array(int)
        impl = array.load_dialect_impl(dialect())
        self.assertTrue(isinstance(impl, VARCHAR))

    def test_process_bind_param_postgresql_passthrough(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        array = Array(int)
        input = object()
        output = array.process_bind_param(input, dialect())
        self.assertTrue(output is input)

    def test_process_bind_param_other_dialect_none(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        array = Array(int)
        self.assertEqual(array.process_bind_param(None, dialect()), None)

    def test_process_bind_param_other_dialect_with_data(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        array = Array(int)
        input = [1, 2, 3]
        output = array.process_bind_param(input, dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, '[1, 2, 3]')

    def test_process_result_postgresql_passthrough(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        array = Array(int)
        input = object()
        output = array.process_result_value(input, dialect())
        self.assertTrue(output is input)

    def test_process_result_value_other_dialect_none(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        array = Array(int)
        self.assertEqual(array.process_result_value(None, dialect()), None)

    def test_process_result_value_other_dialect_with_data(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        array = Array(int)
        input = '[1, 2, 3]'
        output = array.process_result_value(input, dialect())
        self.assertEqual(output, [1, 2, 3])


class ArrayRoundtrip(RoundTripTestCase):
    @classmethod
    def setupClass(cls):
        super(ArrayRoundtrip, cls).setupClass()

        class Frop(cls.BaseObject):
            __tablename__ = 'frop'
            id = schema.Column(types.Integer(), primary_key=True)
            storage = schema.Column(MutableList.as_mutable(Array(int)), default=list)

        cls.Frop = Frop
        cls.metadata.create_all()

    def test_roundtrip(self):
        obj = self.Frop()
        obj.id = 1
        obj.storage = [1, 2, 3]
        self.session.add(obj)
        self.session.flush()
        self.session.expire(obj)
        new = self.session.query(self.Frop).get(1)
        self.assertEqual(new.storage, [1, 2, 3])

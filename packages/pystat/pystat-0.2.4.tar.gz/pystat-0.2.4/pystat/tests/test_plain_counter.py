from __future__ import absolute_import

try:
    from cPickle import loads, dumps
except ImportError:
    from pickle import loads, dumps

from pystat.tests.base import TestCase
from pystat.plain_counter import PlainCounter


class TestPlainCounter(TestCase):

    def setUp(self):
        super(TestPlainCounter, self).setUp()
        self.counter = PlainCounter()

    def test_add(self):
        self.counter.add()
        self.assertEqual(1, len(self.counter))
        self.counter.add()
        self.assertEqual(2, len(self.counter))

    def test_serialization(self):
        self.counter.add()
        self.counter.add()
        self.assertEqual(2, len(self.counter))
        dump = dumps(self.counter)
        counter = loads(dump)
        self.assertEqual(2, len(counter))

    def test_union(self):
        c1 = PlainCounter()
        c2 = PlainCounter()
        c1.add()
        c1.add()
        c2.add()
        c2.add()
        c3 = c1.union(c2)
        self.assertEqual(4, len(c3))

    def test_init(self):
        c = PlainCounter([1, 2, 3])
        self.assertEqual(3, len(c))

    def test_fluent(self):
        c = PlainCounter()
        self.assertIs(c, c.add().add())
        self.assertEqual(2, len(c))

    def test_overflow(self):
        c = PlainCounter()
        c.load(11111111111111111111)
        with self.assertRaises(OverflowError):
            len(c)

    def test_load(self):
        c = PlainCounter()
        c.load(5)
        self.assertEqual(5, len(c))

    def test_dump(self):
        c = PlainCounter([1])
        self.assertEqual(1, c.dump())

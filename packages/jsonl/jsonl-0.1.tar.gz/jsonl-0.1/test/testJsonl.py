import unittest
from jsonl import jsonl

class testJSONL(unittest.TestCase):

    def setUp(self):
        self.tv = '{"a":1}'
        self.tv1 = '{"a":{"b":2}, "c":3}'

    def tearDown(self):
        pass

    def testSimpleAttribute(self):
        r = jsonl.loads(self.tv)
        assert r.a == 1

    def testComplexAttribute(self):
        r = jsonl.loads(self.tv1)
        assert r.a.b == 2
        assert r.c == 3

    def testNamedTuple(self):
        r = jsonl.loads(self.tv1)
        assert r.a.__class__.__name__==jsonl.OBJECT_NAME

if __name__ == '__main__':
    unittest.main()


    #!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_union_find
----------------------------------

Tests for `python_algorithms.union_find` module.
"""

import unittest

from python_algorithms.basic.union_find import UF


class TestUnionFind(unittest.TestCase):

    def setUp(self):
        self.N = 10
        self.uf = UF(self.N)
        self.pairs = ((0, 1), (1, 2), (4, 5), (7, 8), (8, 9))

    def test_count(self):
        self.assertEqual(self.uf.count(), self.N)
        self.assertEqual(self.count_sets(), self.N)

        for x, y in self.pairs:
            self.uf.union(x, y)
        n = self.N - len(self.pairs)
        self.assertEqual(self.uf.count(), n)
        self.assertEqual(self.count_sets(), n)

    def test_find(self):
        for i in range(self.N):
            self.assertEqual(self.uf.find(i), i)

        for x, y in self.pairs:
            self.uf.union(x, y)

        for x, y in self.pairs:
            self.assertEqual(self.uf.find(x), self.uf.find(y))

    def test_connected(self):
        for i in range(self.N):
            for j in range(self.N):
                if i == j:
                    continue
                self.assertFalse(self.uf.connected(i, j))

        for x, y in self.pairs:
            self.uf.union(x, y)

        for x, y in self.pairs:
            self.assertTrue(self.uf.connected(x, y))

    def test_str_empty_uf(self):
        self.assertEqual(str(UF(0)), "")

    def test_str_uf(self):
        s = " ".join([str(x) for x in range(self.N)])
        self.assertEqual(str(self.uf), s)

    def count_sets(self):
        return len(set([self.uf.find(x) for x in range(self.N)]))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()

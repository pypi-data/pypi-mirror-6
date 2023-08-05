import unittest
from gridly import Location as Loc
from gridly import Direction as Dir

class TestLocation(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(Loc.zero(), Loc(0, 0))

    def test_add(self):
        self.assertEqual(Loc(2, 3) + Loc(6, 5), Loc(8, 8))

    def test_subtract(self):
        self.assertEqual(Loc(3, 4) - Loc(1, 1), Loc(2, 3))

    def test_above(self):
        self.assertEqual(Loc(3, 4).above(), Loc(2, 4))

    def test_below(self):
        self.assertEqual(Loc(2, 2).below(), Loc(3, 2))

    def test_left(self):
        self.assertEqual(Loc(3, 3).left(), Loc(3, 2))

    def test_right(self):
        self.assertEqual(Loc(1, 1).right(), Loc(1, 2))

    def test_relative(self):
        self.assertEqual(Loc(1, 1).relative(Dir.down), Loc(2, 1))

    def test_relative_distance(self):
        self.assertEqual(Loc(2, 2).relative(Dir.right, 10), Loc(2, 12))

    def test_path(self):
        start = Loc(3, 4)
        end = start.path(Dir.down, Dir.left, Dir.down)
        self.assertEqual(end, Loc(5, 3))

    def test_adjacent(self):
        adjacent = Loc(0, 0).adjacent()

        for i in (-1, 1):
            self.assertIn(Loc(0, i), adjacent)
            self.assertIn(Loc(i, 0), adjacent)

    def test_diagonal(self):
        diagonals = Loc(0, 0).diagonals()

        for r in (-1, 1):
            for c in (-1, 1):
                self.assertIn(Loc(r, c), diagonals)

    def test_surrounding(self):
        surrounding = Loc(1, 1).surrounding()

        for r in range(3):
            for c in range(3):
                if not (r == 1 and c == 1):
                    self.assertIn(Loc(r, c), surrounding)

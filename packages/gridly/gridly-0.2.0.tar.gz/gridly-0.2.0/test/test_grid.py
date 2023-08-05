from unittest import TestCase
from gridly.grid import DenseGrid, SparseGrid

class GenericGridTests:
    @classmethod
    def setUpClass(cls):
        cls.num_rows = 5
        cls.num_columns = 7

    def setUp(self):
        self.grid = self.grid_type(
            self.num_rows,
            self.num_columns)

    def test_dimensions(self):
        self.assertEqual(self.grid.num_rows, self.num_rows)
        self.assertEqual(self.grid.num_columns, self.num_columns)

    def test_out_of_range(self):
        for row in (-1, self.num_rows):
            for column in (-1, self.num_columns):
                with self.assertRaises(IndexError):
                    value = self.grid[row, column]

    def test_empty_reads(self):
        for row in range(self.num_rows):
            for column in range(self.num_columns):
                self.assertIs(self.grid[row, column], None)

    def test_random_sets(self):
        locations = {
            (1, 1),
            (4, 0),
            (2, 0),
            (0, 1),
            (4, 5),
            (2, 5)
        }

        for location in locations:
            self.grid[location] = 10

        for r, row in enumerate(self.grid.rows()):
            for c, cell in enumerate(row):
                if (r, c) in locations:
                    self.assertEqual(cell, 10)
                else:
                    self.assertIs(cell, None)

    def test_all_sets_row(self):
        for row in range(self.num_rows):
            for column in range(self.num_columns):
                self.grid[row, column] = row

        for r, row in enumerate(self.grid.rows()):
            for cell in row:
                self.assertEqual(cell, r)

    def test_all_sets_column(self):
        for row in range(self.num_rows):
            for column in range(self.num_columns):
                self.grid[row, column] = row

        for column in self.grid.columns():
            for r, cell in enumerate(column):
                self.assertEqual(cell, r)

    def test_reset(self):
        locations = {
            (1, 1),
            (4, 0),
            (2, 0),
            (0, 1),
            (4, 5),
            (2, 5)
        }

        for row in range(self.num_rows):
            for column in range(self.num_columns):
                self.grid[row, column] = 10

        for location in locations:
            self.grid[location] = None

        for r, row in enumerate(self.grid.rows()):
            for c, cell in enumerate(row):
                if (r, c) in locations:
                    self.assertIs(cell, None)
                else:
                    self.assertEqual(cell, 10)

class TestDenseGrid(GenericGridTests, TestCase):
    grid_type = DenseGrid

class TestSparseGrid(GenericGridTests, TestCase):
    grid_type = SparseGrid

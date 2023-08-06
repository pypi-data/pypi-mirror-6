from unittest import TestCase
from gridly import DenseGrid, SparseGrid, CompositeGrid

class TestGenericGrid:
    num_rows = 5
    num_columns = 7

    def test_dimensions(self):
        self.assertEqual(self.grid.num_rows, self.num_rows)
        self.assertEqual(self.grid.num_columns, self.num_columns)

    def test_out_of_range(self):
        for row in (-1, self.num_rows):
            for column in (-1, self.num_columns):
                with self.assertRaises(IndexError):
                    value = self.grid[row, column]

    def test_row_iter_out_of_range(self):
        with self.assertRaises(IndexError):
            row = list(self.grid.row(self.num_rows+10))

    def test_column_iter_out_of_range(self):
        with(self.assertRaises(IndexError)):
            column = list(self.grid.column(self.num_columns-10))

class TestGenericConcreteGrid(TestGenericGrid):
    def setUp(self):
        self.grid = self.grid_type(
            self.num_rows,
            self.num_columns)

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

        for location, cell in self.grid.cells():
            if location in locations:
                self.assertEqual(cell, 10)
            else:
                self.assertIs(cell, None)

    def test_single_row(self):
        row = 3
        for column in range(self.num_columns):
            self.grid[row, column] = 10

        for cell in self.grid.row(row):
            self.assertEqual(cell, 10)

    def test_single_column(self):
        column = 1
        for row in range(self.num_rows):
            self.grid[row, column] = 10

        for cell in self.grid.column(column):
            self.assertEqual(cell, 10)

    def test_row_bounds_check(self):
        self.assertRaises(IndexError, self.grid.row, -1)

    def test_column_bounds_check(self):
        self.assertRaises(IndexError, self.grid.column, -1)

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

    def test_locations(self):
        locations = iter(self.grid.locations())

        for row in range(self.num_rows):
            for column in range(self.num_columns):
                self.assertEqual((row, column), next(locations))

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

class TestDenseGrid(TestGenericConcreteGrid, TestCase):
    grid_type = DenseGrid

class TestSparseGrid(TestGenericConcreteGrid, TestCase):
    grid_type = SparseGrid

class TestCompositeGrid(TestGenericGrid, TestCase):
    def setUp(self):
        self.grid1 = DenseGrid(self.num_rows, self.num_columns)
        self.grid2 = SparseGrid(self.num_rows, self.num_columns)
        self.grid = CompositeGrid(self.grid1, self.grid2)

    def test_get_set(self):
        self.grid[3, 4] = [1, 2]
        self.assertEqual(list(self.grid[3, 4]), [1, 2])
        self.assertEqual(self.grid1[3, 4], 1)
        self.assertEqual(self.grid2[3, 4], 2)

    def test_iter(self):
        for row in self.grid.rows():
            for cell in row:
                cell[0] = 1
                cell[1] = 2

        for row in range(self.num_rows):
            for column in range(self.num_columns):
                self.assertEqual(list(self.grid[row, column]), [1, 2])
                self.assertEqual(self.grid1[row, column], 1)
                self.assertEqual(self.grid2[row, column], 2)

                for layer, i in zip(self.grid[row, column], (1, 2)):
                    self.assertEqual(layer, i)

    def test_dimension_mismatch(self):
        self.grid2 = SparseGrid(self.num_rows+1, self.num_columns+1)
        with self.assertRaises(ValueError):
            self.grid = CompositeGrid(self.grid1, self.grid2)

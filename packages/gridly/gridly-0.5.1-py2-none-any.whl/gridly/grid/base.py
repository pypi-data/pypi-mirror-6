import abc
from gridly import Location


class GridBase(metaclass=abc.ABCMeta):
    '''
    Base class to provide common functionality to Grids. Grid concrete
    classes should implement `unsafe_get` and `unsafe_set`.
    '''

    def __init__(self, num_rows, num_columns, content):
        self._row_range = range(num_rows)
        self._col_range = range(num_columns)
        self.content = content

    @property
    def num_rows(self):
        return len(self._row_range)

    @property
    def num_columns(self):
        return len(self._col_range)

    @property
    def dimensions(self):
        return self.num_rows, self.num_columns

    ####################################################################
    # Bounds Checkers
    ####################################################################

    #TODO: these are inner-loop functions. Determine if they should be optimized.
    def valid_row(self, row):
        '''return true if the row is in the bounds of this grid.'''
        return row in self._row_range

    def valid_column(self, column):
        '''return true if the column is in the bounds of this grid.'''
        return column in self._col_range

    def valid(self, location):
        '''
        Return true if a location is in the bounds of this grid.
        '''
        return self.valid_row(location[0]) and self.valid_column(location[1])

    def check_row(self, row):
        '''
        Return the row if it is in the bounds. Raise IndexError otherwise
        '''
        if self.valid_row(row):
            return row
        else:
            raise IndexError(row)

    def check_column(self, column):
        '''
        Return the row if it is in the bounds. Raise IndexError otherwise
        '''
        if self.valid_column(column):
            return column
        else:
            raise IndexError(column)

    def check_location(self, location):
        '''
        Return the location if it is valid. Raise IndexError otherwise.
        '''
        if self.valid(location):
            return location
        else:
            raise IndexError(location)


    ####################################################################
    # Basic element access
    ####################################################################
    @abc.abstractmethod
    def unsafe_get(self, location):
        raise NotImplementedError

    @abc.abstractmethod
    def unsafe_set(self, location, value):
        raise NotImplementedError

    def __getitem__(self, location):
        '''
        Perform a checked lookup. Raises IndexError if location is out of range.
        '''
        return self.unsafe_get(self.check_location(location))

    def __setitem__(self, location, value):
        '''
        Perform a checked set. Raises IndexError if location is out of range.
        '''
        self.unsafe_set(self.check_location(location), value)


    ####################################################################
    # Iterators
    ####################################################################
    def unsafe_row(self, row):
        '''
        Iterate over all the cells in a row. Performs no range checking.
        '''
        for column in self._col_range:
            yield self.unsafe_get((row, column))

    def unsafe_column(self, column):
        '''
        Iterate over all the cells in a column. Performs no range checking.
        '''
        for row in self._row_range:
            yield self.unsafe_get((row, column))

    def row(self, row):
        '''
        Iterate over all the cells in a row. Raises IndexError if row is out of range
        '''
        return self.unsafe_row(self.check_row(row))

    def column(self, column):
        '''
        Iterate over all the cells in a column
        '''
        return self.unsafe_column(self.check_column(column))

    def rows(self):
        '''
        Iterate over each row. Each row is an iterable, containing each cell in
        the row
        '''
        for row in self._row_range:
            yield self.unsafe_row(row)

    def columns(self):
        '''
        Iterate over each columns. Each column is an iterable, containing each
        cell in the column
        '''
        for column in self._col_range:
            yield self.unsafe_column(column)

    def locations(self):
        '''
        Iterate over each location on the grid
        '''
        for row in self._row_range:
            for column in self._col_range:
                yield Location(row, column)

    def cells(self):
        '''
        Iterate over (location, cell) pairs
        '''
        for location in self.locations():
            yield location, self.unsafe_get(location)

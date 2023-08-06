import abc

def valid_range(value, max):
    '''
    return true if value between 0 and max (max is exclusive)
    '''
    return (0 <= value < max)

def check_or_raise(value, condition, Exception):
    '''
    Returns the value if it meets the condition, otherwise raises and
    Exception
    '''
    if condition(value):
        return value
    else:
        raise Exception(value)

class GridBase(metaclass=abc.ABCMeta):
    '''
    Base class to provide common functionality to Grids. Grid concrete
    classes should implement `unsafe_get` and `unsafe_set`.
    '''

    def __init__(self, num_rows, num_columns, content):
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.content = content

    @property
    def dimensions(self):
        '''
        Get the dimesions as a tuple
        '''
        return self.num_rows, self.num_columns

    ####################################################################
    # Bounds Checkers
    ####################################################################

    #TODO: these are inner-loop functions. Determine if they should be optimized.
    def valid_row(self, row):
        '''return true if the row is in the bounds of this grid.'''
        return valid_range(row, self.num_rows)

    def valid_column(self, column):
        '''return true if the column is in the bounds of this grid.'''
        return valid_range(column, self.num_columns)

    def valid(self, location):
        '''
        Return true if a location is in the bounds of this grid.
        '''
        return self.valid_row(location[0]) and self.valid_column(location[1])

    def check_row(self, row):
        '''
        Return the row if it is in the bounds. Raise IndexError otherwise
        '''
        return check_or_raise(row, self.valid_row, IndexError)

    def check_column(self, column):
        '''
        Return the row if it is in the bounds. Raise IndexError otherwise
        '''
        return check_or_raise(column, self.valid_column, IndexError)

    def check_location(self, location):
        '''
        Return the location if it is valid. Raise IndexError otherwise.
        '''
        return check_or_raise(location, self.valid, IndexError)


    ####################################################################
    # Basic element access
    ####################################################################
    @abc.abstractmethod
    def unsafe_get(self, location):
        raise NotImplementedError

    @abc.abstractmethod
    def unsafe_set(self, location, value):
        raise NotImplementedError

    def get(self, location):
        '''
        Perform a checked lookup. Raises IndexError if location is out of range.
        '''
        return self.unsafe_get(self.check_location(location))

    def set(self, location, value):
        '''
        Perform a checked set. Raises IndexError if location is out of range.
        '''
        self.unsafe_set(self.check_location(location), value)

    def __getitem__(self, location):
        '''
        Perform a checked lookup. Raises IndexError if location is out of range.
        '''
        return self.get(location)

    def __setitem__(self, location, value):
        '''
        Perform a checked set. Raises IndexError if location is out of range.
        '''
        self.set(location, value)


    ####################################################################
    # Iterators
    ####################################################################
    def unsafe_row(self, row):
        '''
        Iterate over all the cells in a row. Performs no range checking.
        '''
        for column in range(self.num_columns):
            yield self.unsafe_get((row, column))

    def unsafe_column(self, column):
        '''
        Iterate over all the cells in a column. Performs no range checking.
        '''
        for row in range(self.num_rows):
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
        for row in range(self.num_rows):
            yield self.unsafe_row(row)

    def columns(self):
        '''
        Iterate over each columns. Each column is an iterable, containing each
        cell in the column
        '''
        for column in range(self.num_columns):
            yield self.unsafe_column(column)

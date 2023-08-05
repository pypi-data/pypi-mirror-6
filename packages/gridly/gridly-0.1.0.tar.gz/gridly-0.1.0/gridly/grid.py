class GridMixin:
    '''
    Mixin to provide common functionality to Grids. Grid concrete classes should
    implement `unsafe_get`, `unsafe_set`, and `__init__(num_rows, num_columns,
    content=content)`
    '''
    def __init__(self, num_rows, num_columns, content):
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.content = content

    def valid(self, location):
        '''
        Return true if a location is valid
        '''
        return (0 <= location[0] < self.num_rows and
            0 <= location[1] < self.num_columns)

    def check_location(self, location):
        '''
        Return location if a location is valid. Raise IndexError otherwise.
        '''
        #TODO: Check back here as a candidate for "inner loop" optimiztion
        if self.valid(location):
            return location
        else:
            raise IndexError(location)

    def __getitem__(self, location):
        return self.unsafe_get(self.check_location(location))

    def __setitem__(self, location, value):
        return self.unsafe_set(self.check_location(location), value)

    def row(self, row):
        '''
        Iterate over all the cells in a row
        '''
        for column in range(self.num_columns):
            yield self.unsafe_get((row, column))

    def column(self, column):
        '''
        Iterate over all the cells in a column
        '''
        for row in range(self.num_rows):
            yield self.unsafe_get((row, column))

    def rows(self):
        '''
        Iterate over each row. Each row is an iterable, containing each cell in
        the row
        '''
        for row in range(self.num_rows):
            yield self.row(row)

    def columns(self):
        '''
        Iterate over each columns. Each column is an iterable, containing each
        cell in the column
        '''
        for column in range(self.num_columns):
            yield self.column(column)

class DenseGrid(GridMixin):
    '''
    DenseGrid is for grids which have content in most of the cells.
    '''
    def __init__(self, num_rows, num_columns, fill=None, content=None):
        if content is None:
            content = [fill] * num_rows * num_columns
        GridMixin.__init__(self, num_rows, num_columns, content)

    def index(self, location):
        '''
        Convert a (row, column) tuple to an index. Performs no bounds checking.
        '''
        return (self.num_columns * location[0]) + location[1]

    def unsafe_get(self, location):
        return self.content[self.index(location)]

    def unsafe_set(self, location, value):
        self.content[self.index(location)] = value


class SparseGrid(GridMixin):
    '''
    SparseGrid is for grids for which most of the cells are some empty, default
    value
    '''
    def __init__(self, num_rows, num_columns, fill=None, content=None):
        if content is None:
            content = {}
        GridMixin.__init__(self, num_rows, num_columns, content)
        self.fill = fill

    def unsafe_get(self, location):
        return self.content.get(location, self.fill)

    def unsafe_set(self, location, value):
        if value is self.fill:
            self.content.pop(location, None)
        else:
            self.content[location] = value

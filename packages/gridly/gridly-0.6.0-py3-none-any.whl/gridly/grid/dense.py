from itertools import repeat, chain, islice
from gridly.grid.base import GridBase

class DenseGrid(GridBase):
    '''
    DenseGrid is for grids which have content in most of the cells. It is
    implemented as a list.
    '''
    def __init__(self, num_rows, num_columns, content=(), fill=None, func=None):
        if func is not None:
            content = [func((row, column))
                for row in range(num_rows)
                for column in range(num_columns)]
        else:
            content = list(islice(chain(content, repeat(fill)),
                num_rows * num_columns))

        GridBase.__init__(self, num_rows, num_columns, content)

    def index(self, location):
        '''
        Convert a (row, column) tuple to an index. Performs no bounds checking.
        '''
        return (self.num_columns * location[0]) + location[1]

    def unsafe_get(self, location):
        return self.content[self.index(location)]

    def unsafe_set(self, location, value):
        self.content[self.index(location)] = value

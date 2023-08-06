from gridly.grid.base import GridBase

class SparseGrid(GridBase):
    '''
    SparseGrid is for grids for which most of the cells are some empty, default
    value. Implemented as a dict.
    '''
    def __init__(self, num_rows, num_columns, fill=None):
        GridBase.__init__(self, num_rows, num_columns, {})
        self.fill = fill

    def unsafe_get(self, location):
        return self.content.get(location, self.fill)

    def unsafe_set(self, location, value):
        if value is self.fill:
            self.content.pop(location, None)
        else:
            self.content[location] = value

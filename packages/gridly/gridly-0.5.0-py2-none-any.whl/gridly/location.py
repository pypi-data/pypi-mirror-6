import collections
from gridly.direction import Direction

class Location(collections.namedtuple('Location', ('row', 'column'))):
    '''
    Location reperesents a location in a 2D row-column space. It is primarily
    a helper class over regular tuples of (row, column). It assumes that +row
    is down and +column is right.
    '''
    @classmethod
    def zero(cls):
        '''
        Create a (0, 0) initialized Location
        '''
        return cls(0, 0)

    def __add__(self, other):
        '''
        Adds 2 Locations, memberwise.
        '''
        return Location(self[0] + other[0], self[1] + other[1])

    def __sub__(self, other):
        '''
        Subtracts 2 Locations, memberwise.
        '''
        return Location(self[0] - other[0], self[1] - other[1])

    def __mul__(self, value):
        '''
        Multiply a location by a factor
        '''
        return Location(self[0] * value, self[1] * value)

    def above(self, distance=1):
        '''
        Return the location above this one, at the specified distance
        '''
        return Location(self[0]-distance, self[1])

    def below(self, distance=1):
        '''
        Return the location below this one, at the specified distance
        '''
        return Location(self[0]+distance, self[1])

    def left(self, distance=1):
        '''
        Return the location to the left of this one, at the specified distance
        '''
        return Location(self[0], self[1]-distance)

    def right(self, distance=1):
        '''
        Return the location to the right of this one, at the specified distance
        '''
        return Location(self[0], self[1]+distance)

    def relative(self, direction, distance):
        '''
        Return the location in a relative Direction and distance
        '''
        return self + (direction.value * distance)

    def adjacent(self):
        '''
        Return a set of the 4 locations adjacent to self.
        '''
        return {self + d for d in ((0, 1), (0, -1), (1, 0), (-1, 0))}

    def diagonals(self):
        '''
        Return a set of the 4 locations diagonaly adjacent to self
        '''
        return {self + d for d in ((1, 1), (-1, 1), (1, -1), (-1, -1))}

    def surrounding(self):
        '''
        Return a set of the 8 locations surrounding self
        '''
        return self.adjacent() | self.diagonals()

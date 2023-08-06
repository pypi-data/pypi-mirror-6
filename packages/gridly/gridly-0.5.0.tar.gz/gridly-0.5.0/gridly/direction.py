import enum
from gridly.location import Location

class Direction(enum.Enum):
    '''Enum to reperesent each of the 4 directions'''
    up = north = Location(-1, 0)
    down = south = Location(1, 0)
    left = west = Location(0, -1)
    right = east = Location(0, 1)

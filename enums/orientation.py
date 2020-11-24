from enum import Enum


class Orientation(Enum):
    EAST, SOUTH, WEST, NORTH = 1, 2, 3, 4

    def left(self):
        return Orientation(self.value - 1) if self.value > 1 else Orientation(4)

    def right(self):
        return Orientation(self.value + 1) if self.value < 4 else Orientation(1)
from enums.orientation import Orientation
from utils.utils import Utils

class Wumpus():
    def __init__(self, loc):
        self.loc = loc
        self.alive = True

    def eaten_by_wumpus(self, x, y):
        return self.alive and self.loc[0] == x and self.loc[1] == y

    def is_alive(self):
        return self.alive

    def is_dead(self):
        return not self.alive

    def kill_wumpus(self):
        self.alive = False

    def is_on_target(self, x, y, orientation):
        return {
            Orientation.EAST: (self.loc[0] > x and self.loc[1] == y),
            Orientation.WEST: (self.loc[0] < x and self.loc[1] == y),
            Orientation.NORTH: (self.loc[0] == x and self.loc[1] > y),
            Orientation.SOUTH: (self.loc[0] == x and self.loc[1] < y)
        }[orientation]

    def print(self):
        Utils.tbl_print([[self.loc, self.alive]], headers=["Location", "Is Alive"])

from utils.utils import P
class Pits():
    def __init__(self, locs):
        self.locs = locs

    def is_pit(self, x, y):
        return P(x, y) in self.locs

    def fell_in_pit(self, x, y):
        return P(x, y) in self.locs

    def print(self):
        print(self.locs)
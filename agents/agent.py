from utils.utils import Utils
from utils.utils import P
from enums.orientation import Orientation

class Agent(object):

    def __init__(self):
        self.orientation = Orientation.EAST
        self.loc = P(0, 0); self.trail = []
        self.arrow, self.alive, self.gold, self.climbed  = True, True, False, False
    
    
    def trace(self, loc):
        self.trail.append(loc)
        
    def turn_left(self):
        self.orientation = self.orientation.left()
        return self

    def turn_right(self):
        self.orientation = self.orientation.right()
        return self

    def move_forward(self, grid_height: int, grid_width: int):
        self.loc = {
            Orientation.EAST: P(min(grid_width - 1, self.loc[0] + 1), self.loc[1]),
            Orientation.WEST: P(max(0, self.loc[0] - 1), self.loc[1]),
            Orientation.NORTH: P(self.loc[0], min(grid_height - 1, self.loc[1] + 1)),
            Orientation.SOUTH: P(self.loc[0], max(0, self.loc[1] - 1))
        }[self.orientation]
        return self
    
    def update_perception(self, stench, breeze):
        return self
        
    def shoot_arrow(self):
        self.arrow = False
        return self

    def has_arrow(self):
        return self.arrow

    def has_gold(self):
        return self.gold
    
    def kill_agent(self):
        self.alive = False
        return self
    
    def grab_gold(self):
        self.gold = True
        return self
    
    def climb_up(self):
        self.climbed = True
        return self

    def is_winner(self):
        return self.climbed and self.gold
    
    def is_alive(self):
        return self.alive
    
    def is_dead(self):
        return self.alive == False
    
    def next_move(self, percept): # given a percept, what should be agent's next move
        return None
        
    
    def print(self):
        Utils.tbl_print([[self.loc,self.orientation, self.alive, self.gold, self.arrow, self.climbed]],
                       headers=["Location", "Facing", "Alive", "Has Gold", "Has Arrow", "Has Climbed"])
        print('\n')

from utils.utils import Utils
from IPython.display import display
from tabulate import tabulate

class Percept():
    def __init__(self, stench, breeze, glitter, bump, scream, terminated, reward):
        self.stench, self.breeze, self.glitter, self.bump = stench, breeze, glitter, bump
        self.scream, self.terminated, self.reward =  scream, terminated, reward
        
    def print(self):
        Utils.print_title('Percept')
        Utils.tbl_print([[self.stench, self.breeze, self.glitter, self.bump, self.scream, self.terminated, self.reward]],
                       headers=["Stench", "Breeze", "Glitter", "Bump", "Scream", "Terminated", "Reward"])
        print('\n')
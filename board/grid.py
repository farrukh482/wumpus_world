from utils.utils import Utils
from utils.utils import P
import random
from tabulate import tabulate
tabulate.WIDE_CHARS_MODE = False

class Grid():
    def __init__(self, width, height):
        self.dirs = Utils.get_direction()
        self.width, self.height = width, height
        self.layout = [[''] * width for _ in range(height)] # initialize grid (width x height) 2d array
   
    def all_locs(self): # all possible grid locations
        return [P(x,y) for x in range(self.width) for y in range(self.width)]
    
    def rand_loc(self): # random location except (0,0)
        return random.choice(self.all_locs()[1:])
    
    def locs_by_prob(self, probability): # find locations by probability
        return [x for x in self.all_locs()[1:] if random.random() < probability]
    
    
    def direction(self, c1, c2):
        dx, dy = c2[0] - c1[0], c2[1] - c1[1]
        return 'none' if (abs(dx) > 1 or abs(dy) > 1) else ('right' if dx == 1 else ( 'left' if dx == -1 else (
            'top' if dy == 1 else ('bottom' if dy == -1 else ''))))

    def grid_preview(self):
        return Utils.tbl_style(Utils.flip_mtx(self.layout),
                               headers=[x for x in range(self.width)], index=[x for x in range(self.height-1, -1, -1)])

    def print_layout(self):
        grid = Grid(self.width, self.height)
        grid.layout = [[str(P(i, j)) for j in range(grid.width)] for i in range(grid.height)]
        grid.print()

    def path_preview(self, path, gold_loc):
        print_layout = [[''] * self.width for _ in range(self.height)]
        if gold_loc != None:
            print_layout[gold_loc[0]][gold_loc[1]] = Utils.get_characters()['gold'] # set gold symbol if location given
        prev_loc = (-1, 0); symbol = self.dirs['target']
        for i, loc in enumerate(path):
            next_loc = (self.width + 9, self.height + 9) if (i + 1) >= len(path) else path[i + 1]
            pre, post = self.direction(prev_loc, loc), self.direction(loc, next_loc)
            sym = '' if post == '' else ('target' if post == 'none' else (pre if pre == post else (
                pre + '_' + post)))
            print_layout[loc[0]][loc[1]] += '' if sym not in self.dirs else (self.dirs[sym] if pre == post else
                                                                                ('{' + self.dirs[sym] + '}'))
            prev_loc = loc
            
        return Utils.tbl_style(Utils.flip_mtx(print_layout),headers=[x for x in range(self.width)], index=[x for x in range(self.height-1, -1, -1)])

    def print_grid_with_path(self, path, gold_loc):
        Utils.hr_tables('Grid Preview', 'Path Preview', self.grid_preview(), self.path_preview(path, gold_loc))
    
    def print_path(self, path, gold_loc):
        Utils.tbl_display(self.path_preview(path, gold_loc))

    def print(self):
        Utils.tbl_display(self.grid_preview())

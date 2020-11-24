# pip install tabulate
from utils.utils import Utils
from board.grid import Grid
from pieces.wumpus import Wumpus
from pieces.gold import Gold
from pieces.pits import Pits
from utils.percept import Percept
from enums.action import Action


class Environment():
    def __init__(self, width, height, pit_prob, agent, climb_without_gold):
        self.chars = Utils.get_characters()
        self.width, self.height, self.pit_prob, self.agent = width, height, pit_prob, agent
        self.climb_without_gold = climb_without_gold
        self.reset()

    def reset(self):
        self.grid = Grid(self.width, self.height)  # set grid
        self.wumpus = Wumpus(self.grid.rand_loc())  # set wumpus
        self.pits = Pits(self.grid.locs_by_prob(self.pit_prob))  # set pits
        self.gold = Gold(self.grid.rand_loc())  # set gold
        self.populate_grid(self.grid)
        return self

    def override(self, wumpus_loc, pits_loc, gold_loc):  # for times when we need to fix locations for experiments
        self.grid = Grid(self.width, self.height)  # set grid
        self.wumpus = Wumpus(wumpus_loc)  # set wumpus
        self.pits = Pits(pits_loc)  # set pits
        self.gold = Gold(gold_loc)  # set gold
        self.populate_grid(self.grid)
        return self

    def populate_grid(self, grid):

        self.grid = grid
        self.grid.layout[self.wumpus.loc[0]][self.wumpus.loc[1]] += (
            self.chars['wumpus'] if self.wumpus.is_alive()
            else self.chars['dead_wumpus'])  # place wumpus on grid
        for loc in Utils.adj_locs(self.wumpus.loc[0], self.wumpus.loc[1], self.width,
                                  self.height):  # set stench in wumpus adjacent cells
            if loc != None:
                self.grid.layout[loc[0]][loc[1]] += self.chars['stench']

        for pit in self.pits.locs:  # set breeze for all pit adjacent cells
            self.grid.layout[pit[0]][pit[1]] += self.chars['pit'] if self.chars['pit'] not in \
                                                                           self.grid.layout[pit[0]][pit[1]] else ''
            for loc in Utils.adj_locs(pit[0], pit[1], self.width, self.height):
                if loc != None:
                    self.grid.layout[loc[0]][loc[1]] += self.chars['breeze'] if self.chars['breeze'] not in \
                                                                                      self.grid.layout[loc[0]][
                                                                                          loc[1]] else ''

        self.grid.layout[self.gold.loc[0]][self.gold.loc[1]] += self.chars['gold']  # place gold on grid
        self.grid.layout[self.agent.loc[0]][self.agent.loc[1]] += self.chars['agent']  # place agent on grid

    def feel_breeze(self):
        return self.chars['breeze'] in self.grid.layout[self.agent.loc[0]][self.agent.loc[1]]

    def smell_stench(self):
        return self.chars['stench'] in self.grid.layout[self.agent.loc[0]][self.agent.loc[1]] or 'W' in \
               self.grid.layout[self.agent.loc[0]][self.agent.loc[1]]

    def see_glitter(self):
        return self.chars['gold'] in self.grid.layout[self.agent.loc[0]][self.agent.loc[1]]

    def current_percept(self):
        return Percept(self.smell_stench(), self.feel_breeze(), self.see_glitter(), False, False, self.agent.is_dead(),
                       0)

    def got_bumped(self, prev_x, prev_y):
        return self.agent.loc[0] == prev_x and self.agent.loc[1] == prev_y

    def process_move(self, action):

        prev_x, prev_y = self.agent.loc[0], self.agent.loc[1]  # store previous location of agent to feel the bump

        if action == Action.LEFT:
            self.agent.turn_left()
            return Percept(self.smell_stench(), self.feel_breeze(), self.see_glitter(), False, False,
                           self.agent.is_dead(), -1)

        if action == Action.RIGHT:
            self.agent.turn_right()
            return Percept(self.smell_stench(), self.feel_breeze(), self.see_glitter(), False, False,
                           self.agent.is_dead(), -1)

        if action == Action.FORWARD:
            # allow agent to move forward
            self.agent.move_forward(self.grid.width, self.grid.height)
            self.populate_grid(Grid(self.width, self.height))  # after agent moves, reflect new reality on grid
            if self.wumpus.eaten_by_wumpus(self.agent.loc[0], self.agent.loc[1]) or self.pits.fell_in_pit(
                    self.agent.loc[0], self.agent.loc[1]):
                self.agent.alive = False

            bumped = self.got_bumped(prev_x, prev_y)
            # update perception of the agent after move
            self.agent.update_perception(self.smell_stench(), self.feel_breeze())
            return Percept(self.smell_stench(), self.feel_breeze(), self.see_glitter(), bumped, False,
                           self.agent.is_dead(), -1 if self.agent.is_alive() else -1001)

        if action == Action.SHOOT:
            scream, used_arrow = False, False
            if self.agent.has_arrow():
                self.agent.shoot_arrow()
                if self.wumpus.is_alive() and self.wumpus.is_on_target(self.agent.loc[0], self.agent.loc[1],
                                                                       self.agent.orientation):
                    self.wumpus.kill_wumpus()
                    wumpus_cell = self.grid.layout[self.wumpus.loc[0]][self.wumpus.loc[1]]
                    wumpus_cell_new = wumpus_cell.replace(self.chars['wumpus'], self.chars['dead_wumpus'])
                    self.grid.layout[self.wumpus.loc[0]][self.wumpus.loc[1]] = wumpus_cell_new
                    self.agent.heard_scream = True
                    scream = True
            return Percept(self.smell_stench(), self.feel_breeze(), self.see_glitter(), False, scream,
                           False, -10 if used_arrow else -1)

        if action == Action.GRAB:
            if self.see_glitter():
                self.agent.grab_gold()
            return Percept(self.smell_stench(), self.feel_breeze(), self.see_glitter(), False, False, False, -1)

        if action == Action.CLIMB:
            if self.climb_without_gold or self.agent.has_gold():
                self.agent.climb_up()
                return Percept(self.smell_stench(), self.feel_breeze(), self.see_glitter(), False, False, True,
                               999 if self.agent.has_gold() else -1)
            else:
                return Percept(self.smell_stench(), self.feel_breeze(), self.see_glitter(), False, False, False, -1)

    def print(self):
        Utils.print_title('Grid')
        print('--legend:{}'.format(self.chars))
        self.grid.print_grid_with_path(self.agent.trace, self.gold.loc)


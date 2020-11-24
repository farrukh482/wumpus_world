from agents.beeline_agent import BeelineAgent
from utils.utils import Utils
from utils.utils import P
from enums.action import Action
from enums.orientation import Orientation

import networkx as nx
from pomegranate import *
from itertools import product
import random


class ProbAgent(BeelineAgent):
    def __init__(self, grid_width = 4, grid_height = 4, pit_prob = 0.2, threshold = 0.5):
        super().__init__()
        self.trace = [P(0, 0)]  # It starts at (0,0), so add init location by default
        self.shortest, self.action_list = [], []
        self.action_list_target_loc = None # for debugging only
        self.graph = nx.DiGraph()
        self.grid_width, self.grid_height = grid_width, grid_height
        self.pit_prob, self.threshold = pit_prob, threshold
        # ProbAgent specific properties

        self.safe_locs, self.breeze_locs, self.stench_locs, self.wumpus_mtx, self.pit_mtx = [P(0,0)], [], [], [], []
        self.heard_scream = False
        self.give_up, self.back_track = False, False
        self.init_dists()

    def init_dists(self):
        self.wumpus_found = False
        self.wumpus_prob = 1.0 / (self.grid_width * self.grid_height - 1)  # any cell but first can have wumpus
        wumpus_cell_dist = DiscreteDistribution({True: self.wumpus_prob, False: (1 - self.wumpus_prob)})
        pit_cell_dist = DiscreteDistribution({True: self.pit_prob, False: (1 - self.pit_prob)})

        self.wumpus_mtx = [[self.wumpus_prob] * self.grid_width for _ in range(self.grid_height)]
        self.pit_mtx = [[self.pit_prob] * self.grid_width for _ in range(self.grid_height)]
        self.wumpus_mtx[0][0] = 0  # first cell has no wumpus
        self.pit_mtx[0][0] = 0  # first cell has no pit

    def update_probabilities(self, stench, breeze):
        cur_wumpus_prob = self.wumpus_mtx[self.loc.i][self.loc.j]
        self.wumpus_mtx[self.loc.i][self.loc.j] = 0
        self.pit_mtx[self.loc.i][self.loc.j] = 0
        
        
        if not any(self.wumpus_mtx[i][j] == 1 for i in range(self.grid_width) for j in range(self.grid_height)):
            self.update_wumpus_probs(stench)
        
        self.update_pit_probs(breeze)
        
        
    def update_pit_probs(self, breeze):
        adj_cells = Utils.adj_locs(self.loc.i, self.loc.j, self.grid_width, 
                                   self.grid_height)  # adjacent cells to current cell
        
        neighbors = [x for x in adj_cells if x is not None] # remove Nones
        
        if not breeze:
            for x in neighbors:
                self.pit_mtx[x.i][x.j] = 0
        else:
            neighbor_probs = self.probability(neighbors, self.pit_mtx)
            for i, n in enumerate(neighbors):
                self.pit_mtx[n.i][n.j] = neighbor_probs[i]
                
        for loc in self.breeze_locs:
            adj_cells = [x for x in Utils.adj_locs(loc.i, loc.j, self.grid_width, self.grid_height) if x is not None]
            if (sum([1 for x in adj_cells if self.pit_mtx[x.i][x.j] > 0]) == 1): # if there is only 1 value greater than 0
                for x in adj_cells:
                    self.pit_mtx[x.i][x.j] = 1 if self.pit_mtx[x.i][x.j] > 0 else 0
                
    def update_wumpus_probs(self, stench):

        wumpus_arr = numpy.array([numpy.array(x) for x in self.wumpus_mtx])

        if self.heard_scream:  # if wumpus is dead, all wumpus probabilities are 0
            self.wumpus_found = True
            wumpus_arr *= 0
            self.wumpus_mtx = wumpus_arr.tolist()
        else:
            wumpus_arr /= self.wumpus_prob
            self.wumpus_prob = 1 / (self.grid_width * self.grid_height - len(self.safe_locs))
            wumpus_arr *= self.wumpus_prob
            self.wumpus_mtx = wumpus_arr.tolist()
            adj_cells = Utils.adj_locs(self.loc.i, self.loc.j, self.grid_width, 
                                       self.grid_height)  # adjacent cells to current cell
            if stench:
                # all cells except adjacent cells to stench have 0 proability of wumpus
                for i in range(self.grid_width):
                    for j in range(self.grid_height):
                        if P(i, j) not in adj_cells:
                            self.wumpus_mtx[i][j] = 0
            
                neighbors = [x for x in adj_cells if x is not None] # remove Nones
                neighbor_probs = self.probability(neighbors, self.wumpus_mtx)
                for i, n in enumerate(neighbors):
                    self.wumpus_mtx[n.i][n.j] = neighbor_probs[i]
                
            for loc in self.stench_locs:
                adj_cells = [x for x in Utils.adj_locs(loc.i, loc.j, self.grid_width, self.grid_height) if x is not None]
                if (sum([1 for x in adj_cells if self.wumpus_mtx[x.i][x.j] > 0]) == 1): # if there is only 1 value greater than 0
                    self.wumpus_found = True
                    for x in adj_cells:
                        self.wumpus_mtx[x.i][x.j] = 1 if self.wumpus_mtx[x.i][x.j] > 0 else 0

            
    def probability(self, locs, mtx):
        
        dists = [mtx[x.i][x.j] for x in locs]
        
        dds = [DiscreteDistribution({True: x, False: (1 - x)}) for x in dists]
        cpt = Node(ConditionalProbabilityTable(self.condition_combos(len(dists) + 1), dds), name='cpt')
        nodes = [Node(x, name='n' + str(i)) for i, x in enumerate(dds)]
        model = BayesianNetwork("wumpusworld")
        model.add_nodes(*nodes)
        model.add_node(cpt)
        for node in nodes:
            model.add_edge(node, cpt)
        model.bake()
        to_predict = [False if x in self.safe_locs else None for x in locs]
        to_predict.append(True)
        beliefs = model.predict_proba([to_predict])
        observed= []
        for i, x in enumerate(locs):
            if to_predict[i] == None:
                observed.append( beliefs[0][i].parameters[0][True] ); # if it was to be predicted, get it from beliefs
            else:
                observed.append( mtx[x.i][x.j] ) # if it was safe location, put it as before
        
        return observed

    def condition_combos(self, size):
        combos = list(map(list, product([True, False], repeat=size)))  # e.g. product('TF', repeat=3) => TTT,TTF,TFT,TFF,FTT,FTF,FFT,FFF
        tbl = [x + [1. if any(x[:-1]) == x[-1] else 0.] for x in
               combos]  # e.g TTT=1,TTF=0,TFT=1,TFF=0,FTT=1,FTF=0,FFT=0,FFF=1
        return tbl

    def move_forward(self, grid_height: int, grid_width: int):
        super().move_forward(grid_height, grid_width)
        if self.is_alive():
            self.update_safe_locations()
        return self

    def calculate_actions(self, path):
        super().calculate_actions(path)
        self.action_list_target_loc = path[-1]
    
    def next_move(self, percept):  # given a percept, what should be agent's next move
        
        if percept.glitter == True and not self.has_gold():  # gold has become available, go home
            self.find_shortest_path()
            self.calculate_actions(self.shortest)
            return Action.GRAB

        elif (self.has_gold() or self.give_up) and self.loc == P(0, 0):  # in this case, game has been won
            return Action.CLIMB

        elif len(self.action_list) > 0:  # if action list has actions to take, pop the stack
            action = self.action_list[0]
            self.action_list = self.action_list[1:]
            self.action_list_target_loc = None if len(self.action_list) == 0 else self.action_list_target_loc 
            return action
        else:
            next_loc, next_action = self.next_best_loc(percept.stench, percept.breeze)
            if next_loc is None and next_action is not None:
                return next_action
            else:
                if next_loc in Utils.adj_locs(self.loc.i, self.loc.j, self.grid_width, self.grid_height):
                    self.calculate_actions([self.loc, next_loc])
                else: # if backtracking becuase a previous location is less risky, use beeline to go back
                    self.back_track = False
                    path = self.find_shortest_path(self.loc, next_loc) # if many actions, find shortest path on beeline
                    self.calculate_actions(path)  # convert next location to actions and call recursively
                    
            if len(self.action_list) > 0:
                return self.next_move(percept)
            else:
                # if no action could be decided based on probabilities, make a random move
                return random.choice([Action.LEFT, Action.RIGHT, Action.FORWARD])

    def next_best_loc(self, stench, breeze):
        best_loc = None # if no strategy works, just go back and climb
        next_action = None
        threshold = self.threshold
        adj_locs = Utils.adj_locs(self.loc[0], self.loc[1], self.grid_width, self.grid_height)
        adj_locs = [x for x in adj_locs if x is not None]  # cleanup locations
        adj_locs_unsafe = [x for x in adj_locs if x not in self.safe_locs]  # cleanup locations
        adj_probs = [self.wumpus_mtx[x[0]][x[1]] + self.pit_mtx[x[0]][x[1]] for x in adj_locs_unsafe]  # add wumpus+pit probs
        min_prob = min(adj_probs) if len(adj_probs) > 0 else 1 # find min probability value
        print('=== Minimum probability found in neighbors: ', min_prob)
        
        if min_prob > threshold and stench and self.has_arrow() and not self.wumpus_found: # worth shooting arrow if stench & wumpus alive 
            # in this situation, we must shoot but should shoot to probe probabilities of most unprobed cells possible
            best_orient, max_locs = None, 0
            for orient in Orientation:
                num_locs = len([x for x in self.get_locs_in_direction(orient, self.loc) if x not in self.safe_locs])
                best_orient = orient if num_locs > max_locs else best_orient
                max_locs = num_locs if num_locs > max_locs else max_locs
            
            next_action = (Action.SHOOT if self.orientation == best_orient # 
                           else (Action.LEFT if self.orientation.left() == best_orient else Action.RIGHT))
            print("=== Was facing: ", self.orientation, ", best to shoot: ", best_orient, ", so taking action: ", next_action)
            return None, next_action
        elif min_prob > threshold or len(adj_locs_unsafe) == 0: # check to see if there is any neighbor of safe locations with less prob.
            due_to = None
            adj_min_prob = min_prob # so far the minimum probability
            for loc in self.safe_locs[:-1][::-1]: # this will reverse all except last location (last is current location)
                adj_locs = [x for x in Utils.adj_locs(loc.i, loc.j, self.grid_width, self.grid_height) 
                            if x is not None and x not in self.safe_locs]
                for x in adj_locs:
                    adj_prob = self.wumpus_mtx[x.i][x.j] + self.pit_mtx[x.i][x.j]
                    print("--- Exploring prob. for neighbor: ", x, ", for safe loc: ", loc)
                    if adj_prob < threshold:
                        best_loc = loc if adj_prob < adj_min_prob else best_loc # find minimum probability from all neghbors of safe locs
                        due_to = x if adj_prob < adj_min_prob else due_to
                        adj_min_prob = adj_prob
                        self.back_track = True
                        print("--- Possible backtrack option: ", best_loc, ", due to ", x)

            print("=== Exhaustive neighbor found: ", best_loc, ", due to: ", due_to)
        elif min_prob < threshold:
            min_prob_locs = [x for i, x in enumerate(adj_locs_unsafe) if adj_probs[i] == min_prob]  # locations with minimum probability
            num_actions_required = [len(self.path_from_to(self.orientation, self.loc, x)[0]) for x in min_prob_locs]
            best_loc = min_prob_locs[num_actions_required.index(min(num_actions_required))] #cell with minimum actions required
        
        if best_loc == None:
            best_loc = P(0,0)
            self.give_up = True
        print("=== Best loc: {}, Best action: {}".format(best_loc, next_action))
        return  best_loc, next_action

    def shoot_arrow(self):
        super().shoot_arrow()
        # the direction in which arrow will travel will have zero probability of wumpus
        x, y = self.loc.i, self.loc.j
        for i in range(self.grid_width):
            for j in range(self.grid_height):
                is_within_arrow_path = {
                    Orientation.EAST: (i > x and j == y),
                    Orientation.WEST: (i < x and j == y),
                    Orientation.NORTH: (i == x and j > y),
                    Orientation.SOUTH: (i == x and j < y)
                }[self.orientation]
                self.wumpus_mtx[i][j] = 0 if is_within_arrow_path else self.wumpus_mtx[i][j]
    
        stench, breeze = (self.loc in self.stench_locs), (self.loc in self.breeze_locs)
        self.update_probabilities(stench, breeze)
    
    def get_locs_in_direction(self, orient, loc):
        w, h = self.grid_width, self.grid_height
        return {
            Orientation.EAST: [P(x,y) for x in range(w) for y in range(h) if (x > loc.i and y == loc.j)],
            Orientation.WEST: [P(x,y) for x in range(w) for y in range(h) if (x < loc.i and y == loc.j)],
            Orientation.NORTH: [P(x,y) for x in range(w) for y in range(h) if (x == loc.i and y > loc.j)],
            Orientation.SOUTH: [P(x,y) for x in range(w) for y in range(h) if (x == loc.i and y < loc.j)]
        }[orient]
    
    def update_safe_locations(self):
        if self.loc not in self.safe_locs:
            self.safe_locs.append(self.loc)

    def update_perception(self, stench, breeze):
        if stench and self.loc not in self.stench_locs:
            self.stench_locs.append(self.loc)
        if breeze and self.loc not in self.breeze_locs:
            self.breeze_locs.append(self.loc)

        self.update_probabilities(stench, breeze)

    def print_prob_mtx(self, mtx):
        return Utils.tbl_style(Utils.flip_mtx([[numpy.round(i, 3) for i in x] for x in mtx]),
                               headers=[x for x in range(self.grid_width)],
                               index=[x for x in range(self.grid_height - 1, -1, -1)])

    def print(self):
        super().print()
        print("--safe locations: ", self.safe_locs)
        print("--stench locations: ", self.stench_locs)
        print("--breeze locations: ", self.breeze_locs)
        Utils.hr_tables('Wumpus Probabilities', 'Pits Probabilities', self.print_prob_mtx(self.wumpus_mtx), self.print_prob_mtx(self.pit_mtx))

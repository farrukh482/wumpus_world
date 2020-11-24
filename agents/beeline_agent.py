from agents.naive_agent import NaiveAgent
from enums.orientation import Orientation
from enums.action import Action
from random import random
import networkx as nx
import matplotlib.pyplot as plt


class BeelineAgent(NaiveAgent):
    def __init__(self):
        super().__init__()
        self.trace = [(0, 0)]  # It starts at (0,0), so add init location by default
        self.shortest = []
        self.action_list = []
        self.graph = nx.DiGraph()

    def find_shortest_path(self, source=None, target=None):
        source = self.trace[-1] if source is None else source # just initializing for defaults
        target = self.trace[0] if target is None else target
        self.graph = nx.DiGraph()

        nodes = list(reversed(self.trace)).copy()
        edges = list(zip(nodes, nodes[1:]))

        self.graph.add_nodes_from(nodes)
        self.graph.add_edges_from(edges)

        self.shortest = nx.shortest_path(self.graph, source=source, target=target)
        return self.shortest

    def draw_graph(self):

        fig = plt.figure(1, figsize=(20, 10))
        plt.clf();
        plt.gca().invert_yaxis;
        plt.gca().invert_xaxis
        fig.suptitle('Directed Graph with Shortest Path (red)', fontsize=24)

        g = nx.DiGraph()  # create new graph to draw
        g.add_nodes_from(self.shortest)
        g.add_nodes_from(self.graph.nodes())  # copy nodes

        shortest_edges = list(zip(self.shortest, self.shortest[1:]))
        g.add_edges_from(shortest_edges)  # add shortest edges for highlighting
        g.add_edges_from(self.graph.edges())  # add all edges

        pos = nx.spring_layout(g)
        nx.draw_networkx_nodes(g, pos=pos, node_shape='H', node_size=1500, node_color='cyan')
        nx.draw_networkx_labels(g, pos=pos, font_color='red')

        nx.draw_networkx_edges(g, pos=pos, edgelist=shortest_edges, edge_color='red', width=12, label='Shortest Path')
        nx.draw_networkx_edges(g, pos=pos, edgelist=self.graph.edges(), edge_color='blue', width=3, label='All Edges')

    def calculate_actions(self, path):
        from_loc = path[0]
        orient = self.orientation
        for to_loc in path[1:]:
            actions, orient = self.path_from_to(orient, from_loc, to_loc)
            self.action_list.extend(actions)
            from_loc = to_loc

    def path_from_to(self, cur_orient, from_loc, to_loc):
        required_actions = []
        to_orient = cur_orient
        dx, dy = (to_loc.i - from_loc.i), (to_loc.j - from_loc.j)
        if not (dx == 0 and dy == 0):  # only apply action if moving to different location
            to_orient = Orientation.EAST if dx == 1 else (Orientation.WEST if dx == -1 else (
                Orientation.NORTH if dy == 1 else (
                    Orientation.SOUTH if dy == -1 else cur_orient)))  # desired orientation

            if not (cur_orient == to_orient):  # if oreintation is not same as desired
                if cur_orient.left() == to_orient:
                    required_actions.append(Action.LEFT);
                elif cur_orient.right() == to_orient:
                    required_actions.append(Action.RIGHT);
                elif cur_orient.left().left() == to_orient:  # opposite orientation is needed
                    required_actions.append(Action.LEFT)
                    required_actions.append(Action.LEFT)
            required_actions.append(Action.FORWARD)  # move forward

        return required_actions, to_orient

    def move_forward(self, grid_height: int, grid_width: int):
        super().move_forward(grid_height, grid_width)
        if not self.has_gold() and (len(self.trace) == 0 or self.loc != self.trace[-1]):
            self.trace.append(self.loc)
        return self

    def next_move(self, percept):  # given a percept, what should be agent's next move
        if percept.glitter == True and not self.has_gold():  # gold has become available, go home
            self.find_shortest_path()
            self.calculate_actions(self.shortest)
            return Action.GRAB

        elif self.has_gold() and self.loc == (0, 0):  # in this case, game has been won
            return Action.CLIMB

        elif self.has_gold() and len(
                self.action_list) > 0:  # if gold has been grabbed, agent not at (0,0), take shortest path actions
            action = self.action_list[0]
            self.action_list = self.action_list[1:]
            return action
        else:
            return random.choice([Action.LEFT, Action.RIGHT, Action.FORWARD, Action.SHOOT])

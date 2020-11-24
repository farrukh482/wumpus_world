from utils.utils import Utils
from agents.agent import Agent
from board.environment import Environment

class Episode:
    def run(agent: Agent, env: Environment):

        rewards = 0
        i = 1
        Utils.print_title('Introduction')
        print('\n---charcters symbols: ', Utils.get_characters())
        print('\n---directions symbols: ', Utils.get_direction())
        percept = env.current_percept()

        Utils.divider(' BOARD LAYOUT ', 'red')
        env.print()
        agent.print()
        percept.print()

        while not percept.terminated:
            action = agent.next_move(percept)
            Utils.divider(' {} - {} '.format(i, action))
            percept = env.process_move(action)
            env.print()
            agent.print()
            percept.print()
            rewards += percept.reward
            print('---beeline trace: ', agent.trace)

            Utils.print_title('Running total: {}'.format(rewards))
            Utils.divider('completed - {}'.format(i), 'green')
            i += 1
        Utils.print_title('Grand Total: {}'.format(rewards))

        if agent.is_winner():

            Utils.hr_tables('Full Path to Gold', 'Shortest Path Back Home',
                            env.grid.path_preview(agent.trace, env.gold.loc),
                            env.grid.path_preview(agent.shortest, env.gold.loc))

            Utils.print_title('Graph of Shortest Path')
            print('---shortest path: ', agent.shortest)
            agent.draw_graph()

        print('--- Use this line to reproduce current environment: ')
        print('env.override( wumpus_loc=' + (str(env.wumpus.loc) +
                                             ', pits_loc=' + str(env.pits.locs) +
                                             ', gold_loc=' + str(env.gold.loc)).replace('(', 'P('), ')')
        return rewards, \
               1 if agent.is_winner() else 0, \
               1 if agent.is_dead() else 0, \
               1 if not agent.is_winner() and agent.is_alive() else 0, \
               1 if env.wumpus.is_dead() else 0, \
               len(env.pits.locs)
# Student: Farrukh Aziz - Assignment 3
# Student ID: qq363177
# Class: SCS_3547_008 Intelligent Agents & Reinforcement Learning

from board.environment import Environment
from agents.probablistic_agent import ProbAgent
from board.episode import Episode
from utils.utils import Utils

# Set this to False, if output tables have question marks in them (i.e. Full Unicode is not supported)
Utils.unicode_supported = False
num_simulations = 1000

width, height = 4, 4
pit_prob = 0.2
threshold_to_move = 0.3
total_rewards, total_wins, total_losses, total_abondons, total_wumpus_kills, total_pits = 0, 0, 0, 0, 0, 0
for i in range(1000):
    Utils.divider("SIMULATION # " + str(i + 1))
    agent = ProbAgent(width, height, pit_prob, threshold_to_move)
    env = Environment(width, height, pit_prob, agent, True)
    rewards, win, loss, abondon, wumpus_kill, pits = Episode.run(agent, env)
    total_rewards += rewards
    total_wins += win
    total_losses += loss
    total_abondons += abondon
    total_wumpus_kills += wumpus_kill
    total_pits += pits

Utils.print_title('~' * 70)
Utils.divider("AGGREGATE STATISTICS FOR " + str(num_simulations) + " RUNS")
Utils.tbl_print([[total_rewards, total_wins, total_losses, total_abondons, total_wumpus_kills, total_pits]],
                headers=['Total Rewards', 'Total Wins', 'Total Losses', 'Total Abondoned', 'Total Wumpus Kills', 'Total Pits Faced'])
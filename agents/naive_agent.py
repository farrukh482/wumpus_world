import random
from agents.agent import Agent
from enums.action import Action

class NaiveAgent(Agent):
    def __init__(self):
        super().__init__()
        
    def next_move(self, percept): # given a percept, what should be agent's next move
        return random.choice([act for act in Action])
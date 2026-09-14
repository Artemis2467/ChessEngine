from environment.board import Board
from environment.move import Move
import random

class TestAgent:
    def __init__(self):
        self.policy = random.Random()

    def choose_action(self, action_list: list[Move]) -> Move:
        return self.policy.choice(action_list)
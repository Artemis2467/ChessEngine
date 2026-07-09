from board import Board
from game import Chess
import json

with open('exception_examiner.json', 'r') as f:
    board_holder = json.load(f)
init_map = board_holder['board']
board = Board(color=board_holder['color'], init_map=init_map)
moves = board.all_moves()
for move in moves:
    print(move)

game = Chess(board_holder['color'], init_map)
game.run(examin_exception=False, show_only=True)


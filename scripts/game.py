import pygame
import sys
import random
import json

from displayedBoard import DisplayedBoard
from board import Board, INIT_MAP


class Chess:
    def __init__(self, color='w', init_map=INIT_MAP):

        pygame.init()
        pygame.display.set_caption('Chess')

        self.screen = pygame.display.set_mode((720, 720))

        self.clock = pygame.time.Clock()

        self.init_map = init_map

        self.color = color

        self.board = Board(self.color, self.init_map)

        self.displayed_board = DisplayedBoard(self, self.board)
        

    def run(self, examin_exception=True, show_only=False):
        count = 0
        check_mate = show_only
        while True:
            count += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    check_mate = True

            self.displayed_board.display_board(self.screen)

            self.displayed_board.display_pieces(self.screen)

            if count % 60 == 0 and not check_mate:
                moves = self.board.all_moves()

                try:
                    self.board.move(moves[random.randint(0, len(moves) - 1 if len(moves) != 1 else 1)])
                except IndexError:
                    self.board.move(moves[0])
                except Exception as e:
                    print(e)
                    check_mate = True
                
                if check_mate and examin_exception:
                    board_holder = {'board': {}, 'color': self.board.legal_moves.color}
                    for piece_name in self.board.pieces:
                        board_holder['board'][piece_name] = self.board.pieces[piece_name].get_pos()
                    with open('exception_examiner.json', 'w') as f:
                        json.dump(board_holder, f)
                
            
            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    Chess().run()

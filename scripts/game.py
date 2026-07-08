import pygame
import sys
import random

from displayedBoard import DisplayedBoard
from board import Board


class Chess:
    def __init__(self):

        pygame.init()
        pygame.display.set_caption('Chess')

        self.screen = pygame.display.set_mode((720, 720))

        self.clock = pygame.time.Clock()

        self.color = "b"

        self.board = Board(self.color)

        self.displayed_board = DisplayedBoard(self, self.board)
        

    def run(self):
        count = 0
        check_mate = False
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
                    self.board.move(moves[random.randint(0, len(moves) - 1)])
                except Exception as e:
                    print(e)
                    check_mate = True
            
            pygame.display.update()
            self.clock.tick(60)

Chess().run()

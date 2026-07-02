import pygame
import sys
import random

from scripts.displayedBoard import DisplayedBoard
from scripts.board import Board


class Chess:
    def __init__(self):

        pygame.init()
        pygame.display.set_caption('Chess')

        self.screen = pygame.display.set_mode((720, 720))

        self.clock = pygame.time.Clock()

        self.board = Board()

        self.color = "w"

        self.displayed_board = DisplayedBoard(self, self.board)

        

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.displayed_board.display_board(self.screen)

            self.displayed_board.display_pieces(self.screen)
            
            pygame.display.update()
            self.clock.tick(60)

Chess().run()

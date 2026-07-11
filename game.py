import pygame
import sys
import random
import json

from chessBoard.displayedBoard import DisplayedBoard
from chessBoard.board import Board, INIT_MAP


class Game:
    def __init__(self, color='w', init_map=INIT_MAP, display_only=False):

        pygame.init()
        pygame.display.set_caption('Chess')

        self.screen = pygame.display.set_mode((720, 720))

        self.clock = pygame.time.Clock()

        self.tile_size = 90

        self.init_map = init_map

        self.display_only = display_only

        self.moved = True

        self.color = color

        self.board = Board(self.color, self.init_map)

        self.displayed_board = DisplayedBoard(self, self.board, self.tile_size)

        self.mouse_square_converter = {values['display_cord']: keys for keys, values in self.displayed_board.board_tile.items()}

        self.mouse_square = 0

        self.to_squares = {}

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    displayed_cord = (mouse_x - mouse_x % self.tile_size, mouse_y - mouse_y % self.tile_size)

                    self.prev_mouse_square = self.mouse_square

                    self.mouse_square = self.mouse_square_converter[displayed_cord]
    
            self.displayed_board.display_board(self.screen)

            self.displayed_board.display_pieces(self.screen)
            
            if not self.display_only:
                if self.moved:
                    self.moved = False
                    moves = self.board.all_moves()

                for cord in self.to_squares:
                    if self.mouse_square == cord:
                        self.board.move(self.to_squares[cord])
                        self.moved = True
                
                ally_cords = set((self.board.white_pieces if self.board.color == 'w' else self.board.black_pieces).get_pos())
                self.to_squares = self.displayed_board.display_legal_moves(self.screen, self.mouse_square, moves, ally_cords)

            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    Game().run()

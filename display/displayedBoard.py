COLOR_BLACK = '#B58863'
COLOR_WHITE = '#F0D9B5'

from display.utils import load_images, load_image
from environment.board import Board
from environment.move import Move
import pygame

class DisplayedBoard:
    def __init__(self, game, board: Board, tile_size = 90):
        self.game = game

        self.tile_surf = pygame.Surface((tile_size, tile_size))

        self.board_tile = {
            8 * row + col + 1: {"display_cord": (col * tile_size, row * tile_size), 'color': COLOR_BLACK if (row + col) % 2 == 1 else COLOR_WHITE} for row in range(8) for col in range(8)
        }

        self.board = board

        self.piece_images = load_images('bases', tile_size)        

    def display_board(self, surf):
        for col in range(8):
            for row in range(8):
                cur_tile = self.board_tile[8 * row + col + 1]
                tile = self.tile_surf
                tile.fill(cur_tile['color'])
                surf.blit(tile, cur_tile['display_cord'])

    def display_pieces(self, surf):
        for piece in self.board.pieces:
            cur_bitboard = self.board.pieces[piece]
            cords = cur_bitboard.get_pos()
            piece_surf = self.piece_images[piece]
            for cord in cords:
                surf.blit(piece_surf, self.board_tile[cord]['display_cord'])    

    def display_legal_moves(self, surf, from_square: int, moves: list[Move], ally_cords: set[int]):
        to_squares: dict[int, Move] = {}
        for move in moves:
            if move.orig in ally_cords and move.orig == from_square:
                to_squares[move.to] = move
                tile = self.tile_surf
                tile.fill("#569300")
                tile.set_alpha(100)
                surf.blit(tile, self.board_tile[move.to]['display_cord'])
        return to_squares
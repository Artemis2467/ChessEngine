from environment.move import Move, Castle, Promote, En_passant
from environment.board import Board

class Uci:
    def __init__(self, board: Board):
        self.board = board
        self.game = []
        horizontal_axis = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.int_to_cord = {i + 1: f'{horizontal_axis[i % 8]}{8 - i // 8}' for i in range(64)}
        self.cord_to_int = {cord: int_ for int_, cord in self.int_to_cord}

    def add_move_uci(self, move: Move):
        move_uci = f'{self.int_to_cord[move.orig]}{self.int_to_cord[move.to]}'
        if isinstance(move, Promote):
            move_uci = move_uci + move.promoted_piece

        self.game.append(move_uci)

        return move_uci

    def get_move_from_uci(self, move_sequence: str) -> Move:
        move_uci = move_sequence.split()[-1]
        self.game.append(move_uci)
        orig = self.cord_to_int[move_uci[0] + move_uci[1]]
        to = self.cord_to_int[move_uci[2] + move_uci[3]]

        piece_moved = self.board.get_piece(orig, 'w' if self.board.color == 'b' else 'b')
        piece_captured = self.board.get_piece(to, self.board.color)

        if piece_moved == 'p':
            if (self.board.color == 'w' and 1 <= to <= 8) or (self.board.color == 'b' and 57 <= to <= 64):
                return Promote(self.board, orig, to, promoted_piece=move_uci[4], captured_piece=piece_captured)

            # en-passant needs to be implemented
        if piece_moved == 'k' and (orig == 5 and (to == 7 or to == 3)) or (orig == 61 and (to == 63 or to == 59)):
            return Castle(self.board, is_short_castle= (to==7 or to == 63))

        return Move(self.board, orig, to, piece_moved, piece_captured)
    
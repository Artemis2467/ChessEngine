from __future__ import annotations

INIT_MAP = {
    'wp': [i for i in range(49, 57)],
    'wr': [57, 64],
    'wn': [58, 63],
    'wb': [59, 62],
    'wq': [60],
    'wk': [61],
    'bp': [i for i in range(9, 17)],
    'br': [1, 8],
    'bn': [2, 7],
    'bb': [3, 6],
    'bq': [4],
    'bk': [5],
}

# INIT_MAP = {
#     'wp': [],
#     'wr': [],
#     'wn': [],
#     'wb': [],
#     'wq': [28],
#     'wk': [21],

#     'bp': [],
#     'br': [],
#     'bn': [],
#     'bb': [],
#     'bq': [43],
#     'bk': [27],
# }

from bitboard import Bitboard, CORD_MAP_INT
from chessLogic import StoreMoves, FindLegalMove

class Move:
    def __init__(self, board: Board, orig: int, to: int, piece: str, captured_piece: str | None=None):
        
        self.color = board.color
        self.board = board
        self.orig = orig
        self.to = to
        self.piece = piece

        self.captured_piece = captured_piece

    def __str__(self):
        return f'piece: {self.piece} \n{Bitboard([self.orig, self.to])}'

    def execute(self):
        self.board.pieces[f'{self.color}{self.piece}'].clear_cord(self.orig)
        if self.captured_piece:
            self.board.pieces[self.captured_piece].clear_cord(self.to)
        self.board.pieces[f'{self.color}{self.piece}'].set_cord(self.to)

        cur_color_piece = self.board.white_pieces if self.color == 'w' else self.board.black_pieces
        other_color_piece = self.board.black_pieces if self.color == 'w' else self.board.white_pieces

        cur_color_piece.clear_cord(self.orig)
        if self.captured_piece:
            other_color_piece.clear_cord(self.to)
        cur_color_piece.set_cord(self.to)

        self.board.all.clear_cord(self.orig)
        self.board.all.set_cord(self.to)

    def remove(self):
        self.board.pieces[f'{self.color}{self.piece}'].set_cord(self.orig)
        if self.captured_piece:
            self.board.pieces[f'{'b' if self.color == 'w' else 'w'}{self.captured_piece}'].set_cord(self.to)
        self.board.pieces[f'{self.color}{self.piece}'].clear_cord(self.to)

        cur_color_piece = self.board.white_pieces if self.color == 'w' else self.board.black_pieces
        other_color_piece = self.board.black_pieces if self.color == 'w' else self.board.white_pieces

        cur_color_piece.set_cord(self.orig)
        if self.captured_piece:
            other_color_piece.set_cord(self.to)
        cur_color_piece.clear_cord(self.to)

        self.board.all.set_cord(self.orig)
        if not self.captured_piece:
            self.board.all.clear_cord(self.to)

    def display(self):
        pass

class Board:
    def __init__(self, color:str='w'):
        
        self.color = color

        # init 12 pieces
        self.pieces = {
            'wp': Bitboard(INIT_MAP['wp']),
            'wr': Bitboard(INIT_MAP['wr']),
            'wb': Bitboard(INIT_MAP['wb']),
            'wn': Bitboard(INIT_MAP['wn']),
            'wq': Bitboard(INIT_MAP['wq']),
            'wk': Bitboard(INIT_MAP['wk']),
            'bp': Bitboard(INIT_MAP['bp']),
            'br': Bitboard(INIT_MAP['br']),
            'bb': Bitboard(INIT_MAP['bb']),
            'bn': Bitboard(INIT_MAP['bn']),
            'bq': Bitboard(INIT_MAP['bq']),
            'bk': Bitboard(INIT_MAP['bk']),
        }

        self.white_pieces = Bitboard()
        self.white_pieces.combine(*[self.pieces[piece] if list(piece)[0] == 'w' else None for piece in self.pieces])

        self.black_pieces = Bitboard()
        self.black_pieces.combine(*[self.pieces[piece] if list(piece)[0] == 'b' else None for piece in self.pieces])

        self.all = Bitboard()
        self.all.combine(self.white_pieces, self.black_pieces)

        self.moves = StoreMoves()

        self.legal_moves = FindLegalMove(self, self.moves, self.color)

    def __str__(self):
        return str(self.all)

    def all_moves(self)->list[Move]:
        foe_color = 'w' if self.color == 'b' else 'b'
        check = False
        all_moves = []
        save_squares = Bitboard()

        all_func = self.legal_moves.get_all_moves()
    
        # check if king is in check
        self.legal_moves.foe, self.legal_moves.ally = self.legal_moves.ally, self.legal_moves.foe
        for piece_name in all_func:
            if piece_name != 'k':
                check_bitboard: Bitboard | tuple = all_func[piece_name](self.pieces[f'{foe_color}{piece_name}'], check_king=True)
                if isinstance(check_bitboard, Bitboard):
                    check = True
                    save_squares.combine(check_bitboard)
        self.legal_moves.foe, self.legal_moves.ally = self.legal_moves.ally, self.legal_moves.foe

        # find moves
        for piece_name in all_func:
            if piece_name == 'k':
                self.legal_moves.all.omit_same(self.pieces[f'{self.color}k'])
            moves, captures = all_func[piece_name](self.pieces[f'{self.color}{piece_name}'])

            # find capture moves
            for from_square, to_squares in captures.items():

                # find checking piece capture
                if check and not piece_name == 'k':
                    to_squares = to_squares.find_same(save_squares)

                # check if king can capture checking piece (protected)
                if check and piece_name == 'k':
                    
                    markers: Bitboard = to_squares.copy()
                    self.legal_moves.color = foe_color
                    self.legal_moves.foe, self.legal_moves.ally = self.legal_moves.ally, self.legal_moves.foe
                    self.legal_moves.foe.board |= to_squares.board
                    for foe_piece in all_func:
                        foe_moves, foe_captures = all_func[foe_piece](self.pieces[f'{foe_color}{foe_piece}'])
                        for from_square_foe, to_squares_foe in foe_captures.items():
                            to_squares.omit_same(to_squares_foe)
                    self.legal_moves.foe.omit_same(markers)
                    self.legal_moves.foe, self.legal_moves.ally = self.legal_moves.ally, self.legal_moves.foe
                    self.legal_moves.color = self.color
                
                # add capture moves
                for to_square in to_squares.get_pos():
                    for piece in self.pieces:
                        if list(piece)[0] == foe_color and (self.pieces[piece].board & CORD_MAP_INT[to_square]):
                            all_moves.append(Move(self, from_square, to_square, piece_name, captured_piece=piece))
            
            # find non-capture moves
            for from_square, to_squares in moves.items():

                # find moves that block checks
                if check and not piece_name == 'k':
                    to_squares = to_squares.find_same(save_squares)
                for to_square in to_squares.get_pos():
                    all_moves.append(Move(self, from_square, to_square, piece_name))
            if piece_name == 'k':
                self.legal_moves.all.combine(self.pieces[f'{self.color}k'])
        return all_moves
    
    def move(self, move: Move):
        move.execute()
        self.color = 'w' if self.color == 'b' else 'b'
        self.legal_moves = FindLegalMove(self, self.moves, self.color)

# board = Board(color='b')
# moves = board.all_moves()
# for bitboard in moves:
#     print(bitboard)
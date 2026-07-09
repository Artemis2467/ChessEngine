from __future__ import annotations
from typing import overload, Union, Literal

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

from bitboard import Bitboard, CORD_MAP_INT
from chessLogic import StoreMoves, FindLegalMove

class Move:
    def __init__(self, board: Board, orig: int, to: int, piece: str, captured_piece: str | None=None):
        
        self.color = board.color
        self.board = board
        self.cur_color_piece = self.board.white_pieces if self.color == 'w' else self.board.black_pieces
        self.other_color_piece = self.board.black_pieces if self.color == 'w' else self.board.white_pieces
        
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

        self.cur_color_piece.clear_cord(self.orig)
        if self.captured_piece:
            self.other_color_piece.clear_cord(self.to)
        self.cur_color_piece.set_cord(self.to)

        self.board.all.clear_cord(self.orig)
        self.board.all.set_cord(self.to)

    def remove(self):
        self.board.pieces[f'{self.color}{self.piece}'].set_cord(self.orig)
        if self.captured_piece:
            self.board.pieces[f'{'b' if self.color == 'w' else 'w'}{self.captured_piece}'].set_cord(self.to)
        self.board.pieces[f'{self.color}{self.piece}'].clear_cord(self.to)

        self.cur_color_piece.set_cord(self.orig)
        if self.captured_piece:
            self.other_color_piece.set_cord(self.to)
        self.cur_color_piece.clear_cord(self.to)

        self.board.all.set_cord(self.orig)
        if not self.captured_piece:
            self.board.all.clear_cord(self.to)

    def display(self):
        pass

class Castle(Move):
    def __init__(self, board: Board, is_short_castle: bool):
        if board.color == 'w' and is_short_castle:
            king_orig, king_to = 61, 63
            rook_orig, rook_to = 64, 62
        elif board.color == 'w' and not is_short_castle:
            king_orig, king_to = 61, 59
            rook_orig, rook_to = 57, 60
        elif board.color == 'b' and is_short_castle:
            king_orig, king_to = 5, 7
            rook_orig, rook_to = 8, 6
        elif board.color == 'b' and not is_short_castle:
            king_orig, king_to = 5, 3
            rook_orig, rook_to = 1, 4
        
        super().__init__(board, orig=king_orig, to=king_to, piece='k')
        self.rook_orig, self.rook_to = rook_orig, rook_to
        self.is_short_castle = is_short_castle

    def execute(self):
        super().execute()

        self.board.pieces[f'{self.color}r'].clear_cord(self.rook_orig)
        self.board.pieces[f'{self.color}r'].set_cord(self.rook_to)
        
        self.cur_color_piece.clear_cord(self.rook_orig)
        self.cur_color_piece.set_cord(self.rook_to)

        self.board.all.clear_cord(self.rook_orig)
        self.board.all.set_cord(self.rook_to)

    def __str__(self):
        return f'{'short' if self.is_short_castle else 'long'} castle: \n{Bitboard([self.orig, self.to])}'



class Board:
    def __init__(self, color:str='w', init_map=INIT_MAP):

        self.init_map = init_map
        
        self.color = color

        # init 12 pieces
        self.pieces = {
            'wp': Bitboard(self.init_map['wp']),
            'wr': Bitboard(self.init_map['wr']),
            'wb': Bitboard(self.init_map['wb']),
            'wn': Bitboard(self.init_map['wn']),
            'wq': Bitboard(self.init_map['wq']),
            'wk': Bitboard(self.init_map['wk']),
            'bp': Bitboard(self.init_map['bp']),
            'br': Bitboard(self.init_map['br']),
            'bb': Bitboard(self.init_map['bb']),
            'bn': Bitboard(self.init_map['bn']),
            'bq': Bitboard(self.init_map['bq']),
            'bk': Bitboard(self.init_map['bk']),
        }

        self.white_pieces = Bitboard()
        self.white_pieces.combine(*[self.pieces[piece] if list(piece)[0] == 'w' else None for piece in self.pieces])

        self.black_pieces = Bitboard()
        self.black_pieces.combine(*[self.pieces[piece] if list(piece)[0] == 'b' else None for piece in self.pieces])

        self.all = Bitboard()
        self.all.combine(self.white_pieces, self.black_pieces)

        self.moves = StoreMoves()

        self.legal_moves = FindLegalMove(self, self.moves, self.color)

        self.castle_possible = {'b': {'long': True, 'short': True}, 'w': {'long': True, 'short': True}}

    def __str__(self):
        return str(self.all)
    
    @overload
    def is_in_check(self, foe_color, find_save_squares: Literal[False]=False)->bool: ...

    @overload
    def is_in_check(self, foe_color, find_save_squares: Literal[True])->tuple[int, bool, Bitboard, Bitboard]: ...
    
    def is_in_check(self, foe_color, find_save_squares=False)->Union[bool, tuple[int, bool, Bitboard, Bitboard]]:
        check = False
        check_count = 0
        if find_save_squares:
            save_squares = Bitboard()
            foe_moves = Bitboard()
        all_func = self.legal_moves.get_all_moves()
    
        self.legal_moves.foe, self.legal_moves.ally = self.legal_moves.ally, self.legal_moves.foe
        for piece_name in all_func:
            if piece_name != 'k':
                check_bitboard: Bitboard | tuple = all_func[piece_name](self.pieces[f'{foe_color}{piece_name}'], check_king=True)
                if not check and isinstance(check_bitboard, Bitboard):
                    check = True
                    if find_save_squares:
                        check_count = 1
                        save_squares.combine(check_bitboard)
                elif find_save_squares and isinstance(check_bitboard, tuple):
                    moves, captures = check_bitboard
                    for from_square, to_squares in moves.items():
                        foe_moves.combine(to_squares)
                elif isinstance(check_bitboard, Bitboard) and check:
                    check_count += 1
                    save_squares.combine(check_bitboard)
                if check and not find_save_squares:
                    self.legal_moves.foe, self.legal_moves.ally = self.legal_moves.ally, self.legal_moves.foe
                    return True

        self.legal_moves.foe, self.legal_moves.ally = self.legal_moves.ally, self.legal_moves.foe

        if not check and not find_save_squares:
            return False
        return check_count, check, save_squares, foe_moves


    def all_moves(self)->list[Move]:
        foe_color = 'w' if self.color == 'b' else 'b'
        all_moves: list[Move] = []

        all_func = self.legal_moves.get_all_moves()
    
        # check if king is in check
        check_count, check, save_squares, foe_moves = self.is_in_check(foe_color, find_save_squares=True)
        
        # find moves
        for piece_name in all_func:
            if piece_name == 'k':
                self.legal_moves.all.omit_same(self.pieces[f'{self.color}k']) # avoid king being in the path of attacking piece
            moves, captures = all_func[piece_name](self.pieces[f'{self.color}{piece_name}'])

            # find capture moves
            for from_square, to_squares in captures.items():

                # find checking piece capture
                if check and not piece_name == 'k':
                    to_squares = to_squares.find_same(save_squares)
                    if check_count < 2:
                        to_squares = to_squares.find_same(save_squares)
                    else:
                        to_squares.empty()
                
                # add capture moves
                for to_square in to_squares.get_pos():
                    for piece in self.pieces:
                        if list(piece)[0] == foe_color and (self.pieces[piece].board & CORD_MAP_INT[to_square]):
                            self.legal_moves.all.clear_cord(from_square)
                            self.legal_moves.pieces[piece].clear_cord(to_square)
                            self.legal_moves.ally.set_cord(to_square)
                            if piece_name == 'k':
                                self.legal_moves.pieces[f'{self.color}k'].clear_cord(from_square)
                                self.legal_moves.pieces[f'{self.color}k'].set_cord(to_square)
                            if not self.is_in_check(foe_color):
                                all_moves.append(Move(self, from_square, to_square, piece_name, captured_piece=piece))
                            self.legal_moves.all.set_cord(from_square)
                            self.legal_moves.pieces[piece].set_cord(to_square)
                            self.legal_moves.ally.clear_cord(to_square)
                            if piece_name == 'k':
                                self.legal_moves.pieces[f'{self.color}k'].set_cord(from_square)
                                self.legal_moves.pieces[f'{self.color}k'].clear_cord(to_square)
            
            # find non-capture moves
            for from_square, to_squares in moves.items():

                # find moves that block checks
                if check and not piece_name == 'k':
                    if check_count < 2:
                        to_squares = to_squares.find_same(save_squares)
                    else:
                        to_squares.empty()
                for to_square in to_squares.get_pos():
                    self.legal_moves.all.clear_cord(from_square)
                    self.legal_moves.all.set_cord(to_square)
                    if piece_name == 'k':
                        self.legal_moves.pieces[f'{self.color}k'].clear_cord(from_square)
                        self.legal_moves.pieces[f'{self.color}k'].set_cord(to_square)
                    if not self.is_in_check(foe_color):
                        all_moves.append(Move(self, from_square, to_square, piece_name))
                    self.legal_moves.all.set_cord(from_square)
                    self.legal_moves.all.clear_cord(to_square)
                    if piece_name == 'k':
                        self.legal_moves.pieces[f'{self.color}k'].set_cord(from_square)
                        self.legal_moves.pieces[f'{self.color}k'].clear_cord(to_square)
            if piece_name == 'k':
                self.legal_moves.all.combine(self.pieces[f'{self.color}k'])

        # castle
        king_pos = self.pieces[f"{self.color}k"].get_pos()[0]
        castle_squares = self.moves.get_king_bitboard(king_pos)['castle'][self.color]['short']
        castle_condition = not check and not castle_squares.find_same(foe_moves) and not castle_squares.find_same(self.all)
        if castle_condition and self.castle_possible[self.color]['short']:
            all_moves.append(Castle(self, is_short_castle=True))
        castle_squares = self.moves.get_king_bitboard(king_pos)['castle'][self.color]['long']
        if castle_condition and self.castle_possible[self.color]['long']:
            all_moves.append(Castle(self, is_short_castle=False))
        
        return all_moves
    
    def move(self, move: Move):
        move.execute()
        if move.piece == 'r':
            match move.orig:
                case 1:
                    self.castle_possible['b']['long'] = False
                case 8:
                    self.castle_possible['b']['short'] = False
                case 57:
                    self.castle_possible['w']['long'] = False
                case 64:
                    self.castle_possible['w']['short'] = False
        if move.piece == 'k':
            match move.orig:
                case 61:
                    self.castle_possible['w']['long'] = False
                    self.castle_possible['w']['short'] = False
                case 5:
                    self.castle_possible['b']['long'] = False
                    self.castle_possible['b']['short'] = False

        self.color = 'w' if self.color == 'b' else 'b'
        self.legal_moves = FindLegalMove(self, self.moves, self.color)

# board = Board(color='b')
# moves = board.all_moves()
# for bitboard in moves:
#     print(bitboard)
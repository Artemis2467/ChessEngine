from __future__ import annotations
from typing import overload, Union, Literal

# INIT_MAP = {
#     'wp': [i for i in range(49, 57)],
#     'wr': [57, 64],
#     'wn': [58, 63],
#     'wb': [59, 62],
#     'wq': [60],
#     'wk': [61],
#     'bp': [i for i in range(9, 17)],
#     'br': [1, 8],
#     'bn': [2, 7],
#     'bb': [3, 6],
#     'bq': [4],
#     'bk': [5],
# }


INIT_MAP = {
    'wp': [35],
    'wr': [49],
    'wn': [],
    'wb': [],
    'wq': [],
    'wk': [61],
    'bp': [],
    'br': [],
    'bn': [],
    'bb': [],
    'bq': [40],
    'bk': [2],
}


from environment.bitboard import Bitboard, CORD_MAP_INT
from environment.chessLogic import StoreMoves, FindLegalMove
from environment.move import Move, Castle, Promote, En_passant

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

        self.sequence: list[Move] = []

        self.moves = StoreMoves()

        self.legal_moves = FindLegalMove(self, self.moves, self.color)

        self.castle_possible = {'b': {'long': True, 'short': True}, 'w': {'long': True, 'short': True}}

    def get_piece(self, pos:int, color:str | None=None):
        if color:
            for piece_type in self.pieces:
                if piece_type[0] == color and pos in self.pieces[piece_type].get_pos():
                    return piece_type[1]
        else:
            for piece_type in self.pieces:
                if pos in self.pieces[piece_type].get_pos():
                    return piece_type[1]
        return None

    def __str__(self):
        return str(self.all)

    def en_passant(self):
        try:
            last_move = self.sequence[-1]
        except IndexError:
            return None
        if last_move.piece == 'p':
            if self.color == 'w' and 9 <= last_move.orig <= 16 and 25 <= last_move.to <= 32:

                # left side of target pawn not the edge of the board
                if last_move.to % 8 != 1:
                    en_passant_pawn_square = Bitboard([last_move.to - 1])
                    if self.pieces['wp'].find_same(en_passant_pawn_square):
                        return En_passant(self, orig=last_move.to - 1, to=last_move.to - 8)

                # right side of pawn not the edge of the board
                if last_move.to % 8 != 0:
                    en_passant_pawn_square = Bitboard([last_move.to + 1])
                    if self.pieces['wp'].find_same(en_passant_pawn_square):
                        return En_passant(self, orig=last_move.to + 1, to=last_move.to - 8)

            if self.color == 'b' and 49 <= last_move.orig <= 56 and 33 <= last_move.to <= 40:

                if last_move.to % 8 != 1:
                    en_passant_pawn_square = Bitboard([last_move.to - 1])
                    if self.pieces['bp'].find_same(en_passant_pawn_square):
                        return En_passant(self, orig=last_move - 1, to=last_move.to + 8)

                if last_move.to % 8 != 0:
                    en_passant_pawn_square = Bitboard([last_move.to + 1])
                    if self.pieces['bp'].find_same(en_passant_pawn_square):
                        return En_passant(self, orig=last_move.to + 1, to=last_move.to + 8)

        return None
    
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

        self.legal_moves.color = foe_color
        self.legal_moves.foe, self.legal_moves.ally = self.legal_moves.ally, self.legal_moves.foe
        for piece_name in all_func:
            if piece_name != 'k':
                check_bitboard: Bitboard | tuple = all_func[piece_name](self.pieces[f'{foe_color}{piece_name}'], check_king=True)
                if not check and isinstance(check_bitboard, Bitboard):
                    if not find_save_squares:
                        self.legal_moves.foe, self.legal_moves.ally = self.legal_moves.ally, self.legal_moves.foe
                        self.legal_moves.color = self.color
                        return True
                    check = True
                    check_count = 1
                    save_squares.combine(check_bitboard)
                elif find_save_squares and isinstance(check_bitboard, tuple):
                    moves, captures = check_bitboard
                    for from_square, to_squares in moves.items():
                        foe_moves.combine(to_squares)
                elif isinstance(check_bitboard, Bitboard) and check:
                    check_count += 1
                    save_squares.combine(check_bitboard)

        self.legal_moves.foe, self.legal_moves.ally = self.legal_moves.ally, self.legal_moves.foe
        self.legal_moves.color = self.color

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
                promotion_possible = piece_name == 'p' and ((self.color == 'w' and 9 <= from_square <= 16) or (self.color == 'b' and 49 <= from_square <= 56))

                # find checking piece capture
                if check and not piece_name == 'k':
                    to_squares = to_squares.find_same(save_squares)
                    if check_count < 2:
                        to_squares = to_squares.find_same(save_squares)
                    else: # double checks cannot be solved by capturing or blocking, only by moving the king
                        to_squares.empty()
                
                # add capture moves
                for to_square in to_squares.get_pos():
                    for piece in self.pieces:
                        if list(piece)[0] == foe_color and (self.pieces[piece].board & CORD_MAP_INT[to_square]): # find the captured piece
                            
                            # check if the move results the king being in check
                            self.legal_moves.all.clear_cord(from_square)
                            self.legal_moves.pieces[piece].clear_cord(to_square)
                            self.legal_moves.ally.set_cord(to_square)
                            if piece_name == 'k': # keep the king from blocking future checks
                                self.legal_moves.pieces[f'{self.color}k'].clear_cord(from_square)
                                self.legal_moves.pieces[f'{self.color}k'].set_cord(to_square)
                            if not self.is_in_check(foe_color):
                                # pawn promotion logic
                                if promotion_possible:
                                    for promoted_piece in all_func:
                                        if promoted_piece not in {'k', 'p'}:
                                            all_moves.append(Promote(self, from_square, to_square, promoted_piece=promoted_piece, captured_piece=piece))
                                else:
                                    all_moves.append(Move(self, from_square, to_square, piece_name, captured_piece=piece))
                            # return to previous position
                            self.legal_moves.all.set_cord(from_square)
                            self.legal_moves.pieces[piece].set_cord(to_square)
                            self.legal_moves.ally.clear_cord(to_square)
                            if piece_name == 'k':
                                self.legal_moves.pieces[f'{self.color}k'].set_cord(from_square)
                                self.legal_moves.pieces[f'{self.color}k'].clear_cord(to_square)
                            
            
            # find non-capture moves
            for from_square, to_squares in moves.items():
                promotion_possible = piece_name == 'p' and ((self.color == 'w' and 9 <= from_square <= 16) or (self.color == 'b' and 49 <= from_square <= 56))

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
                        if promotion_possible:
                            for promoted_piece in all_func:
                                if promoted_piece not in {'k', 'p'}:
                                    all_moves.append(Promote(self, from_square, to_square, promoted_piece=promoted_piece))
                        else:
                            all_moves.append(Move(self, from_square, to_square, piece_name))
                    self.legal_moves.all.set_cord(from_square)
                    self.legal_moves.all.clear_cord(to_square)
                    if piece_name == 'k':
                        self.legal_moves.pieces[f'{self.color}k'].set_cord(from_square)
                        self.legal_moves.pieces[f'{self.color}k'].clear_cord(to_square)
            if piece_name == 'k':
                self.legal_moves.all.combine(self.pieces[f'{self.color}k'])

        if not check:
            # castle
            king_pos = self.pieces[f"{self.color}k"].get_pos()[0]
            castle_squares = self.moves.get_king_bitboard(king_pos)['castle'][self.color]['short'] # check conditions
            if not castle_squares.find_same(foe_moves) and not castle_squares.find_same(self.all) and self.castle_possible[self.color]['short']:
                all_moves.append(Castle(self, is_short_castle=True))
            castle_squares = self.moves.get_king_bitboard(king_pos)['castle'][self.color]['long']
            if not castle_squares.find_same(foe_moves) and not castle_squares.find_same(self.all) and self.castle_possible[self.color]['long']:
                all_moves.append(Castle(self, is_short_castle=False))

            # en passant
            en_passant = self.en_passant()
            if isinstance(en_passant, En_passant):
                all_moves.append(en_passant)
        
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
        self.legal_moves = FindLegalMove(self, StoreMoves(), self.color)
        self.sequence.append(move)
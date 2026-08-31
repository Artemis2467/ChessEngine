from environment.bitboard import Bitboard

class Move:
    def __init__(self, board, orig: int, to: int, piece: str, captured_piece: str | None=None): 
        # piece can only be q, k, n, b, r, p, no color is needed
        
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
    def __init__(self, board, is_short_castle: bool):
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

    def __str__(self):
        return f'{'short' if self.is_short_castle else 'long'} castle: \n{Bitboard([self.orig, self.to])}'

    def execute(self):
        super().execute()

        self.board.pieces[f'{self.color}r'].clear_cord(self.rook_orig)
        self.board.pieces[f'{self.color}r'].set_cord(self.rook_to)
        
        self.cur_color_piece.clear_cord(self.rook_orig)
        self.cur_color_piece.set_cord(self.rook_to)

        self.board.all.clear_cord(self.rook_orig)
        self.board.all.set_cord(self.rook_to)

    def remove(self):
        pass

class Promote(Move):
    def __init__(self, board, orig: int, to: int, promoted_piece, captured_piece: str | None=None): # captured piece needs complete piece string
        super().__init__(board, orig, to, piece='p', captured_piece=captured_piece)

        self.promoted_piece = promoted_piece

    def __str__(self):
        return super().__str__()

    def execute(self):
        self.board.pieces[f'{self.color}{self.piece}'].clear_cord(self.orig)
        if self.captured_piece:
            self.board.pieces[self.captured_piece].clear_cord(self.to)
        self.board.pieces[f'{self.color}{self.promoted_piece}'].set_cord(self.to)

        self.cur_color_piece.clear_cord(self.orig)
        if self.captured_piece:
            self.other_color_piece.clear_cord(self.to)
        self.cur_color_piece.set_cord(self.to)

        self.board.all.clear_cord(self.orig)
        self.board.all.set_cord(self.to)

    def remove(self):
        pass

class En_passant(Move):
    def __init__(self, board, orig: int, to: int):
        super().__init__(board, orig, to, piece='p', captured_piece=f'{'w' if board.color == 'b' else 'b'}p')
        self.captured_square = self.to + 8 if self.board.color == 'w' else self.to - 8

    def __str__(self):
        return super().__str__()

    def execute(self):

        self.board.pieces[f'{self.color}{self.piece}'].clear_cord(self.orig)
        self.board.pieces[self.captured_piece].clear_cord(self.captured_square)
        self.board.pieces[f'{self.color}{self.piece}'].set_cord(self.to)

        self.cur_color_piece.clear_cord(self.orig)
        self.other_color_piece.clear_cord(self.captured_square)
        self.cur_color_piece.set_cord(self.to)

        self.board.all.clear_cord(self.orig)
        self.board.all.clear_cord(self.captured_square)
        self.board.all.set_cord(self.to)
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

from bitboard import Bitboard

class Board:
    def __init__(self):

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

        self.white_pieces = Bitboard([])
        self.white_pieces.combine(*[self.pieces[piece] if list(piece)[0] == 'w' else None for piece in self.pieces])

        self.black_pieces = Bitboard([])
        self.black_pieces.combine(*[self.pieces[piece] if list(piece)[0] == 'b' else None for piece in self.pieces])

        self.board = Bitboard([])
        self.board.combine(self.white_pieces, self.black_pieces)
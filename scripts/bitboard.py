from __future__ import annotations

CORD_MAP_INT = {
   8 * row + col + 1: 1 << (64 - (8 * row + col + 1)) for col in range(0, 8) for row in range(0, 8)
}
CORD_MAP_BIN = {
1 << (64 - (8 * row + col + 1)): 8 * row + col + 1 for col in range(0, 8) for row in range(0, 8)
}


class Bitboard:
    def __init__(self, cords: list[int] = []):
        self.board = 0

        for cord in cords:
            self.board |= CORD_MAP_INT[cord]

    def __str__(self):
        orig = list(bin(self.board))[2:]
        board = ['0' for i in range(64 - len(orig))] + orig
        for i in range(56, 0, -8):
            board.insert(i, '\n')
        return ''.join(board)
    
    def __bool__(self)->bool:
        return bool(self.board)
    
    def copy(self):
        res = Bitboard()
        res.combine(self)
        return res
    
    def set_cord(self, cord):
        self.board |= CORD_MAP_INT[cord]

    def clear_cord(self, cord):
        self.board &= ~CORD_MAP_INT[cord]

    def omit_same(self, bitboard: Bitboard):
        self.board &= ~ (bitboard.board & self.board)

    def find_same(self, *args: Bitboard)->Bitboard:
        res = self.copy()
        for arg in args:
            res.board &= arg.board
        return res

    def combine(self, *args: Bitboard | None):
        for arg in args:
            if arg:
                self.board |= arg.board
    
    def get_pos(self)->list[int]:
        positions = []
        board = self.copy()
        while board:
            pos = board.board & -board.board
            board.clear_cord(CORD_MAP_BIN[pos])
            positions.append(CORD_MAP_BIN[pos])
        return positions
    
    def empty(self):
        self.board = 0



        
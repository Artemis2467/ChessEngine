from __future__ import annotations
from bitboard import Bitboard, CORD_MAP_INT

KNIGHT_ATTACKS = [
    -17, -15, 15, 17, -10, -6, 6, 10
]
KING_ATTACKS = [
    -9, -8, -7, -1, 1, 7, 8, 9
]

class StoreMoves:
    def __init__(self):
        self.all_moves = {'n': {}, 'b': {}, 'k': {}, 'r': {}, 'q': {}, 'p': {'w': {}, 'b': {}}}

        for pos in range(1, 65):
            row = (pos - 1) // 8
            col = pos % 8 if pos % 8 != 0 else 8

            # knight
            n_attacks = []
            for attack_offset in KNIGHT_ATTACKS:
                n_attack = pos + attack_offset
                attack_col = n_attack % 8
                if (n_attack > 0 and n_attack <= 64) and not ((1 <= col <= 2 and (attack_col == 7 or attack_col == 0)) or (7 <= col <= 8 and 1 <= attack_col <= 2)):
                    n_attacks.append(n_attack)
            self.all_moves['n'][pos] = Bitboard(n_attacks)

            # rook
            r_attacks = []
            for row_square in range(row * 8 + 1, (row + 1) * 8 + 1):
                if row_square != pos:
                    r_attacks.append(row_square)
            for col_square in range(col, 65, 8):
                if col_square != pos:
                    r_attacks.append(col_square)
            self.all_moves['r'][pos] = Bitboard(r_attacks)

            # biship
            b_attacks = []
            b_attack = pos - 7
            while 0 < b_attack and b_attack % 8 != 1:
                b_attacks.append(b_attack)
                b_attack -= 7
            b_attack = pos - 9
            while 0 < b_attack and b_attack % 8 != 0:
                b_attacks.append(b_attack)
                b_attack -= 9
            b_attack = pos + 9
            while b_attack <= 64 and b_attack % 8 != 1:
                b_attacks.append(b_attack)
                b_attack += 9
            b_attack = pos + 7
            while b_attack <= 64 and b_attack % 8 != 0:
                b_attacks.append(b_attack)
                b_attack += 7        
            self.all_moves['b'][pos] = Bitboard(b_attacks)

            # queen
            q_attacks = Bitboard()
            q_attacks.combine(self.all_moves['b'][pos], self.all_moves['r'][pos])
            self.all_moves['q'][pos] = q_attacks

            # king
            k_attacks = []
            for attack_offset in KING_ATTACKS:
                k_attack = pos + attack_offset
                attack_col = k_attack % 8
                if 1 <= k_attack <= 64 and not ((col == 1 and attack_col == 0) or (col == 8 and attack_col == 1)):
                    k_attacks.append(k_attack)

            wcastle = {'long': Bitboard([i for i in range(57, 62)]), 'short': Bitboard([i for i in range(61, 65)])}
            bcastle = {'long': Bitboard([i for i in range(1, 6)]), 'short': Bitboard([i for i in range(5, 9)])}
            self.all_moves['k'][pos] = {'move': Bitboard(k_attacks), 'castle': {'b': bcastle, 'w': wcastle}}

            # pawn white
            wpawn_moves = []
            wpawn_attacks = []
            en_passant = []
            if 9 <= pos <= 56:
                # attack
                if pos not in {9, 17, 25, 33, 41, 49}:
                    wpawn_attacks.append(pos - 9)
                    # en passant
                    if pos in {i for i in range(25, 33)}:
                        en_passant.append(pos - 1)
                if pos not in {16, 24, 32, 40, 48, 56}:
                    wpawn_attacks.append(pos - 7)
                    if pos in {i for i in range(25, 33)}:
                        en_passant.append(pos + 1)
                # move
                wpawn_moves.append(pos - 8)
                if 49 <= pos <= 56:
                    wpawn_moves.append(pos - 16)

                self.all_moves['p']['w'][pos] = {'move': Bitboard(wpawn_moves), 'attack': Bitboard(wpawn_attacks), 'en_passant': Bitboard(en_passant)}

            # pawn black
            bpawn_moves = []
            bpawn_attacks = []
            en_passant = []
            if 9 <= pos <= 56:

                if pos not in {9, 17, 25, 33, 41, 49}:
                    bpawn_attacks.append(pos + 7)
                    if pos in {i for i in range(33, 41)}:
                        en_passant.append(pos - 1)
                if pos not in {16, 24, 32, 40, 48, 56}:
                    if pos in {i for i in range(33, 41)}:
                        en_passant.append(pos + 1)
                    bpawn_attacks.append(pos + 9)

                bpawn_moves.append(pos + 8)
                if 9 <= pos <= 16:
                    bpawn_moves.append(pos + 16)       
                self.all_moves['p']['b'][pos] = {"move": Bitboard(bpawn_moves), "attack": Bitboard(bpawn_attacks), 'en_passant': Bitboard(en_passant)}
    
    def get_king_bitboard(self, pos: int)->dict[str, Bitboard]:
        return self.all_moves['k'][pos].copy()
    
    def get_knight_bitboard(self, pos: int)->Bitboard:
        return self.all_moves['n'][pos].copy()
    
    def get_pawn_bitboard(self, pos: int, color: str)->dict[str, Bitboard]:
        return self.all_moves['p'][color][pos].copy()
    
    # sliding pieces
    def get_rook_bitboard(self, pos: int)->Bitboard:
        return self.all_moves['r'][pos].copy()
    
    def get_biship_bitboard(self, pos: int)->Bitboard:
        return self.all_moves['b'][pos].copy()
    
    def get_queen_bitboard(self, pos: int)->Bitboard:
        return self.all_moves['q'][pos].copy()

class FindLegalMove:
    def __init__(self, board, moves: StoreMoves, color: str):
        self.moves = moves
        self.color = color
        
        self.pieces:dict[str, Bitboard] = board.pieces
        self.king: Bitboard = board.pieces[f'{self.color}k']
        self.all: Bitboard = board.all
        self.ally: Bitboard = board.white_pieces if self.color == 'w' else board.black_pieces
        self.foe: Bitboard = board.black_pieces if self.color == 'w' else board.white_pieces

    def knight_move(self, knights: Bitboard, check_king: bool=False)->tuple[dict[int, Bitboard], dict[int, Bitboard]] | Bitboard:
        positions = knights.get_pos()
        moves = {}
        captures = {}
        for pos in positions:
            move = self.moves.get_knight_bitboard(pos)
            if check_king and self.king.board & move.board:
                return Bitboard([pos])
            captures[pos] = move.find_same(self.foe)
            move.omit_same(self.all)
            moves[pos] = move

        return moves, captures 
    
    def king_move(self, king: Bitboard)->tuple[dict[int, Bitboard], dict[int, Bitboard]]:
        pos = king.get_pos()[0]
        moves = self.moves.get_king_bitboard(pos)['move']
        all_func = self.get_all_moves()
        all_moves = Bitboard()
        for piece_name in all_func:
            if piece_name != 'k':
                piece_moves, captures = all_func[piece_name](self.pieces[f"{'w' if self.color == 'b' else 'b'}{piece_name}"])
                for bitboard in piece_moves.values():
                    all_moves.combine(bitboard)
            else:
                king_bitboard = self.moves.get_king_bitboard(self.pieces[f'{'w' if self.color == 'b' else 'b'}k'].get_pos()[0])['move']
                moves.omit_same(king_bitboard)

        moves.omit_same(all_moves)
        captures = moves.find_same(self.foe)
        moves.omit_same(self.all)
        return {pos: moves}, {pos: captures}

    def pawn_move(self, pawns: Bitboard, check_king: bool=False)->tuple[dict[int, Bitboard], dict[int, Bitboard]] | Bitboard:
        positions = pawns.get_pos()
        moves = {}
        captures = {}
        for pos in positions:

            ## move
            move = self.moves.get_pawn_bitboard(pos, self.color)['move']
            overlap = move.find_same(self.all)
            if overlap:  
                if self.color == 'w' and 49 <= pos <= 56 and overlap.get_pos()[0] == pos - 8:
                        move.board = 0
                elif self.color == 'b' and 9 <= pos <= 16 and overlap.get_pos()[0] == pos + 8:
                        move.board = 0
                else:
                    move.omit_same(self.all)

            ## captures
            capture = self.moves.get_pawn_bitboard(pos, self.color)['attack']
            if check_king and capture.board & self.king.board:
                return Bitboard([pos])
            capture = capture.find_same(self.foe)

            captures[pos] = capture
            moves[pos] = move
        return moves, captures

    # sliding pieces
    def rook_move(self, rooks:Bitboard, check_king: bool=False)->tuple[dict[int, Bitboard], dict[int, Bitboard]] | Bitboard:
        positions = rooks.get_pos()
        captures = {}
        moves = {}
        for rook_pos in positions:
            row = (rook_pos - 1) // 8 + 1 # starts from 1
            col = rook_pos % 8 if rook_pos % 8 != 0 else 8

            move = self.moves.get_rook_bitboard(rook_pos)
            overlapped = set(move.find_same(self.all).get_pos())
            overlapped_foe = set(move.find_same(self.foe).get_pos())
            blocked = []
            capture = []
            direction_args = [
                (rook_pos + 1, 8 * row + 1), (rook_pos - 1, 8 * (row - 1), -1), (rook_pos - 8, col - 1, -8), (rook_pos + 8, 57 + col, 8)
            ]
            for direction in direction_args:
                first_overlap = 0
                if check_king:
                    connecting_line = [rook_pos]
                for square in range(*direction):
                    if square in overlapped and not first_overlap:
                        first_overlap = square
                        if check_king and CORD_MAP_INT[first_overlap] & self.king.board:
                            return Bitboard(connecting_line)
                    if check_king:
                        connecting_line.append(square)
                    if first_overlap:
                        blocked.append(square)
                if first_overlap in overlapped_foe:
                    capture.append(first_overlap)
            blocked = Bitboard(blocked)

            move.omit_same(blocked)

            moves[rook_pos] = move 
            captures[rook_pos] = Bitboard(capture)

        return moves, captures

    def biship_move(self, biships: Bitboard, check_king: bool=False)->tuple[dict[int, Bitboard], dict[int, Bitboard]] | Bitboard:
        positions = biships.get_pos()
        moves = {}
        captures = {}
        for biship_pos in positions:

            move = self.moves.get_biship_bitboard(biship_pos)
            overlapped = set(move.find_same(self.all).get_pos())
            overlapped_foe = set(move.find_same(self.foe).get_pos())
            blocked = []
            capture = []
            direction_args = [
                (biship_pos - 7, 0, -7), (biship_pos + 9, 65, 9), (biship_pos - 9, 0, -9), (biship_pos + 7, 65, 7)
            ]

            for direction in direction_args:
                first_overlap = 0
                if check_king:
                    connecting_line = [biship_pos]
                for square in range(*direction):
                    if square in overlapped and not first_overlap:
                        first_overlap = square
                        if check_king and CORD_MAP_INT[first_overlap] & self.king.board:
                            return Bitboard(connecting_line)
                    if check_king:
                        connecting_line.append(square)
                    if first_overlap:
                        blocked.append(square)
                    if square % 8 == 0 or square % 8 == 1:
                        break
                    
                if first_overlap in overlapped_foe:
                    capture.append(first_overlap)

            blocked = Bitboard(blocked)
            move.omit_same(blocked)
            capture = Bitboard(capture)

            moves[biship_pos] = move
            captures[biship_pos] = capture
                    
        return moves, captures

    def queen_move(self, queens:Bitboard, check_king: bool=False)->tuple[dict[int, Bitboard], dict[int, Bitboard]] | Bitboard:
        positions = queens.get_pos()
        moves = {}
        captures = {}
        for queen_pos in positions:
            row = (queen_pos - 1) // 8 + 1 # starts from 1
            col = queen_pos % 8 if queen_pos % 8 != 0 else 8

            move = self.moves.get_queen_bitboard(queen_pos)
            overlapped = set(move.find_same(self.all).get_pos())
            overlapped_foe = set(move.find_same(self.foe).get_pos())
            blocked = []
            capture = []
            rook_direction_args = [
                (queen_pos + 1, 8 * row + 1), (queen_pos - 1, 8 * (row - 1), -1), (queen_pos - 8, col - 1, -8), (queen_pos + 8, 57 + col, 8),  
            ]
            biship_direction_args = [
                (queen_pos - 7, 0, -7), (queen_pos + 9, 65, 9), (queen_pos - 9, 0, -9), (queen_pos + 7, 65, 7),
            ]
            for direction in rook_direction_args:
                first_overlap = 0
                if check_king:
                    connecting_line = [queen_pos]
                for square in range(*direction):
                    if square in overlapped and not first_overlap:
                        first_overlap = square
                        if check_king and CORD_MAP_INT[first_overlap] & self.king.board:
                            return Bitboard(connecting_line)
                    if check_king:
                        connecting_line.append(square)
                    if first_overlap:
                        blocked.append(square)
                if first_overlap in overlapped_foe:
                    capture.append(first_overlap)
            for direction in biship_direction_args:
                first_overlap = 0
                if check_king:
                    connecting_line = [queen_pos]
                for square in range(*direction):
                    if square in overlapped and not first_overlap:
                        first_overlap = square
                        if check_king and CORD_MAP_INT[first_overlap] & self.king.board:
                            return Bitboard(connecting_line)
                    if check_king:
                        connecting_line.append(square)
                    if first_overlap:
                        blocked.append(square)
                    if square % 8 == 0 or square % 8 == 1:
                        break
                if first_overlap in overlapped_foe:
                    capture.append(first_overlap)

            blocked = Bitboard(blocked)

            move.omit_same(blocked)

            moves[queen_pos] = move 

            captures[queen_pos] = Bitboard(capture)

        return moves, captures
    
    def get_all_moves(self):
        all_moves = {
            'k': self.king_move,
            'q': self.queen_move,
            'r': self.rook_move,
            'b': self.biship_move,
            'n': self.knight_move,
            'p': self.pawn_move,
        }
        return all_moves
    

# board = Board()
# moves = StoreMoves()
# legal_moves = FindLegalMove(board, moves, color='w')

# rook_moves = legal_moves.rook_move(board.pieces['wr'])
# moves, captures = rook_moves if isinstance(rook_moves, tuple) else ({}, {})
# for from_square, to_squares in moves.items():
#     print(to_squares)
#     print('\n')

# for from_square, to_squares in captures.items():
#     print(to_squares)
#     print('\n')
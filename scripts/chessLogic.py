from bitboard import Bitboard, CORD_MAP_INT
from board import Board

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
            q_attacks = Bitboard([])
            q_attacks.combine(self.all_moves['b'][pos], self.all_moves['r'][pos])
            self.all_moves['q'][pos] = q_attacks

            # king
            k_attacks = []
            for attack_offset in KING_ATTACKS:
                k_attack = pos + attack_offset
                attack_col = k_attack % 8
                if 1 <= k_attack <= 64 and not ((col == 1 and attack_col == 0) or (col == 8 and attack_col == 1)):
                    k_attacks.append(k_attack)
            self.all_moves['k'][pos] = Bitboard(k_attacks)

            # pawn white
            wpawn_moves = []
            wpawn_attacks = []
            if 9 <= pos <= 56:

                if pos not in {9, 17, 25, 33, 41, 49}:
                    wpawn_attacks.append(pos - 9)
                if pos not in {16, 24, 32, 40, 48, 56}:
                    wpawn_attacks.append(pos - 7)
                
                wpawn_moves.append(pos - 8)
                if 49 <= pos <= 56:
                    wpawn_moves.append(pos - 16)
                self.all_moves['p']['w'][pos] = {'move': Bitboard(wpawn_moves), 'attack': Bitboard(wpawn_attacks)}

            # pawn black
            bpawn_moves = []
            bpawn_attacks = []
            if 9 <= pos <= 56:

                if pos not in {9, 17, 25, 33, 41, 49}:
                    bpawn_attacks.append(pos + 7)
                if pos not in {16, 24, 32, 40, 48, 56}:
                    bpawn_attacks.append(pos + 9)

                bpawn_moves.append(pos + 8)
                if 9 <= pos <= 16:
                    bpawn_moves.append(pos + 16)       
                self.all_moves['p']['b'][pos] = {"move": Bitboard(bpawn_moves), "attack": Bitboard(bpawn_attacks)}
    
    def get_king_bitboard(self, pos: int)->Bitboard:
        return self.all_moves['k'][pos]
    
    def get_knight_bitboard(self, pos: int)->Bitboard:
        return self.all_moves['n'][pos]
    
    def get_pawn_bitboard(self, pos: int, color: str)->dict[str, Bitboard]:
        return self.all_moves['p'][color][pos]
    
    # sliding pieces
    def get_rook_bitboard(self, pos: int)->Bitboard:
        return self.all_moves['r'][pos]
    
    def get_biship_bitboard(self, pos: int)->Bitboard:
        return self.all_moves['b'][pos]
    
    def get_queen_bitboard(self, pos: int)->Bitboard:
        return self.all_moves['q'][pos]

class FindLegalMove:
    def __init__(self, board: Board, moves: StoreMoves, color: str):
        self.moves = moves
        self.color = color
        self.board = board

        self.ally = self.board.white_pieces if self.color == 'w' else self.board.black_pieces
        self.foe = self.board.black_pieces if self.color == 'w' else self.board.white_pieces

    def update(self, board, color):
        self.color = color

        # a new FindLegalMove class should be created every move to update self.board
        # otherwise update() function is used for calculations
        self.ally = board.white_pieces if self.color == 'w' else self.board.black_pieces
        self.foe = board.black_pieces if self.color == 'w' else self.board.white_pieces

    def knight_move(self, knights: Bitboard):
        positions = knights.get_pos()
        attacks = {}
        for pos in positions:
            attack = self.moves.get_knight_bitboard(pos)
            attack.omit_same(self.ally)
            attacks[pos] = attack
        return attacks
    
    def king_move(self, king: Bitboard):
        position = king.get_pos()[0]
        attack = self.moves.get_king_bitboard(position)
        attack.omit_same(self.ally)
        return {position: attack}

    def pawn_move(self, pawns: Bitboard):
        positions = pawns.get_pos()
        moves = {}
        for pos in positions:

            # move
            move = self.moves.get_pawn_bitboard(pos, self.color)['move']
            overlap_with_ally = move.find_same(self.ally)
            overlap_with_foe = move.find_same(self.foe)
            if overlap_with_ally:  
                if self.color == 'w' and 49 <= pos <= 56 and overlap_with_ally.get_pos()[0] == pos - 8:
                        move.board = 0
                elif self.color == 'b' and 9 <= pos <= 16 and overlap_with_ally.get_pos()[0] == pos + 8:
                        move.board = 0
                else:
                    move.omit_same(self.ally)
            if overlap_with_foe:  
                if self.color == 'w' and 49 <= pos <= 56 and overlap_with_foe.get_pos()[0] == pos - 8:
                        move.board = 0
                elif self.color == 'b' and 9 <= pos <= 16 and overlap_with_foe.get_pos()[0] == pos + 8:
                        move.board = 0
                else:
                    move.omit_same(self.foe)

            # attack
            attack = self.moves.get_pawn_bitboard(pos, self.color)['attack']
            attack_foe = attack.find_same(self.foe)
            move.board |= attack_foe.board
            
            moves[pos] = move
        return moves

    # sliding pieces
    def rook_move(self, rooks:Bitboard)->dict:
        positions = rooks.get_pos()
        attacks = {}
        for rook_pos in positions:
            row = (rook_pos - 1) // 8 + 1 # starts from 1
            col = rook_pos % 8 if rook_pos % 8 != 0 else 8

            attack = self.moves.get_rook_bitboard(rook_pos)
            overlapped_ally = attack.find_same(self.ally)
            overlapped_foe = attack.find_same(self.foe)
            overlapped_positions = set(overlapped_ally.get_pos()).union(set(overlapped_foe.get_pos()))
            blocked = []
            # right
            right = 0
            for square in range(rook_pos, 8 * row + 1):
                if square in overlapped_positions and not right:
                    right = square
                if right:
                    blocked.append(square)
            # left
            left = 0
            for square in range(rook_pos - 1, 8 * (row - 1), -1):
                if square in overlapped_positions:
                    left = square
                    break
            # up
            up = 0
            for square in range(rook_pos - 8, col - 1, -8):
                if square in overlapped_positions:
                    up = square
                    break
            # down
            down = 0
            for square in range(rook_pos + 8, 57 + col, 8):
                if square in overlapped_positions:
                    down = square
                    break

        return attacks

    def biship_move(self):
        pass

    def queen_move(self):
        pass

# board = Board()
# move_generator = FindLegalMove(board, StoreMoves(), 'w')
# for piece, board in move_generator.pawn_move(board.pieces['wp']).items():
#     print(piece)
#     print(board)

moves = StoreMoves()
board = Board()
legal_moves = FindLegalMove(board, moves, 'w')
for move, bitboard in legal_moves.pawn_move(board.pieces['wp']).items():
    print(move)
    print(bitboard)


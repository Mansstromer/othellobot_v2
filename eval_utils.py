from moves_utils import get_moves
from jit_utils import legal_moves_jit
import numpy as np

SQUARE_W = [
   20, -3, 11,  8,  8, 11, -3, 20,
   -3, -7, -4,  1,  1, -4, -7, -3,
   11, -4,  2,  2,  2,  2, -4, 11,
    8,  1,  2, -3, -3,  2,  1,  8,
    8,  1,  2, -3, -3,  2,  1,  8,
   11, -4,  2,  2,  2,  2, -4, 11,
   -3, -7, -4,  1,  1, -4, -7, -3,
   20, -3, 11,  8,  8, 11, -3, 20,
]

def evaluate(board, player):
    my_bb  = board.black if player == 1 else board.white
    opp_bb = board.white if player == 1 else board.black

    # positional
    pos = 0
    for i, w in enumerate(SQUARE_W):
        mask = 1 << (63 - i)
        if my_bb & mask:   pos += w
        elif opp_bb & mask: pos -= w

    # mobility
    my_m  = int(bin(int(legal_moves_jit(np.uint64(my_bb),  np.uint64(opp_bb)))).count('1'))
    opp_m = int(bin(int(legal_moves_jit(np.uint64(opp_bb), np.uint64(my_bb)))).count('1'))
    mob   = (my_m - opp_m) * 5

    # corners
    corners, corner_score = [0, 7, 56, 63], 0
    for c in corners:
        mask = 1 << c
        if my_bb & mask:      corner_score += 25
        elif opp_bb & mask:   corner_score -= 25

    return pos + mob + corner_score
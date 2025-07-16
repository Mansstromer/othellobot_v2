# moves_utils.py

import numpy as np
from board import Board
from jit_utils import legal_moves_jit


def get_moves(board: Board, player: int) -> list[int]:
    """
    Return list of legal move indices (0–63) for `player` (1=black, -1=white)
    using the JIT-compiled bitboard generator.
    """
    us = np.uint64(board.black if player == 1 else board.white)
    them = np.uint64(board.white if player == 1 else board.black)
    moves_bb = legal_moves_jit(us, them)

    moves = []
    bb = int(moves_bb)
    while bb:
        lsb = bb & -bb
        idx = lsb.bit_length() - 1
        moves.append(idx)
        bb ^= lsb
    return moves

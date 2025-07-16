# moves_utils.py

import numpy as np
from board import Board
from jit_utils import legal_moves_jit

def get_moves(board: Board, player: int) -> list[int]:
    """
    Return list of legal move indices (0–63) for `player`
    using the Numba-JIT bitboard generator.
    """
    us   = np.uint64(board.black if player == 1 else board.white)
    them = np.uint64(board.white if player == 1 else board.black)
    raw  = legal_moves_jit(us, them)

    # raw is a uint64-like from Numba; int(raw) works at runtime.
    # Add a local ignore so Pylance doesn’t complain.
    bb = int(raw)  # type: ignore

    moves = []
    while bb:
        lsb = bb & -bb
        moves.append(lsb.bit_length() - 1)
        bb ^= lsb
    return moves
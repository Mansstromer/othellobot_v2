# moves_utils.py

import numpy as np
from board import Board
from jit_utils import legal_moves_jit


def get_moves(board: Board, player: int) -> list[int]:
    """Return list of legal move indices (0–63) for `player` using the
    Numba-JIT bitboard generator."""
    us = np.uint64(board.black if player == 1 else board.white)
    them = np.uint64(board.white if player == 1 else board.black)
    raw = legal_moves_jit(us, them)

    # raw is a uint64-like from Numba; int(raw) works at runtime.
    bb = int(raw)  # type: ignore

    moves: list[int] = []
    while bb:
        lsb = bb & -bb
        bit_index = lsb.bit_length() - 1
        moves.append(bit_index)
        bb ^= lsb
    return moves

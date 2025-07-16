import numpy as np
from board import Board
from jit_utils import legal_moves_jit

def get_moves(board: Board, player: int) -> list[int]:
    """Return legal moves (0-63) using JIT’d bitboard generator."""
    us   = np.uint64(board.black if player == 1 else board.white)
    them = np.uint64(board.white if player == 1 else board.black)
    bb   = int(legal_moves_jit(us, them))

    moves = []
    while bb:
        lsb = bb & -bb
        moves.append(lsb.bit_length() - 1)
        bb ^= lsb
    return moves
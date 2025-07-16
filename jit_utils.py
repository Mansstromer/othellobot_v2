# jit_utils.py
from numba import njit, uint64, int64

@njit(uint64(uint64, uint64, int64, uint64), cache=True, fastmath=True)
def directional_fill(gen, prop, shift, mask):
    """
    Helper for bitboard flipping using Kogge-Stone algorithm.
    gen: uint64 generator bitboard
    prop: uint64 pieces to propagate through
    shift: int64 signed shift amount
    mask: uint64 edge mask
    Returns a uint64 flip mask.
    """
    flip = prop & mask & (gen << shift if shift > 0 else gen >> -shift)
    flip |= prop & mask & (flip << shift if shift > 0 else flip >> -shift)
    flip |= prop & mask & (flip << shift if shift > 0 else flip >> -shift)
    return flip

@njit(uint64(uint64, uint64), cache=True, fastmath=True)
def legal_moves_jit(us, them):
    """
    JIT-compiled bitboard legal-move generator (unrolled directions).
    us, them: uint64 bitboards.
    Returns a uint64 bitboard of legal moves.
    """
    empty = ~(us | them) & uint64(0xFFFFFFFFFFFFFFFF)
    moves_bb = uint64(0)

    # North (shift 8)
    prop = directional_fill(us, them, int64(8), uint64(0xFFFFFFFFFFFFFF00))
    moves_bb |= prop << int64(8)
    # South (shift -8)
    prop = directional_fill(us, them, int64(-8), uint64(0x00FFFFFFFFFFFFFF))
    moves_bb |= prop >> int64(8)
    # East (shift 1)
    prop = directional_fill(us, them, int64(1), uint64(0x7F7F7F7F7F7F7F7F))
    moves_bb |= prop << int64(1)
    # West (shift -1)
    prop = directional_fill(us, them, int64(-1), uint64(0xFEFEFEFEFEFEFEFE))
    moves_bb |= prop >> int64(1)
    # NE (shift 9)
    prop = directional_fill(us, them, int64(9), uint64(0x007F7F7F7F7F7F00))
    moves_bb |= prop << int64(9)
    # NW (shift 7)
    prop = directional_fill(us, them, int64(7), uint64(0x00FEFEFEFEFEFE00))
    moves_bb |= prop << int64(7)
    # SE (shift -7)
    prop = directional_fill(us, them, int64(-7), uint64(0x7F7F7F7F7F7F7F00))
    moves_bb |= prop >> int64(7)
    # SW (shift -9)
    prop = directional_fill(us, them, int64(-9), uint64(0xFEFEFEFEFEFEFE00))
    moves_bb |= prop >> int64(9)

    return moves_bb & empty

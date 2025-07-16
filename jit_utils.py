from numba import njit, uint64, int64

@njit(uint64(uint64, uint64, int64, uint64), cache=True, fastmath=True)
def directional_fill(gen, prop, shift, mask):
    flip = prop & mask & (gen << shift if shift > 0 else gen >> -shift)
    flip |= prop & mask & (flip << shift if shift > 0 else flip >> -shift)
    flip |= prop & mask & (flip << shift if shift > 0 else flip >> -shift)
    return flip

@njit(uint64(uint64, uint64), cache=True, fastmath=True)
def legal_moves_jit(us, them):
    empty   = ~(us | them) & uint64(0xFFFFFFFFFFFFFFFF)
    moves   = uint64(0)

    # N
    p = directional_fill(us, them,  8, uint64(0xFFFFFFFFFFFFFF00)); moves |= p <<  8
    # S
    p = directional_fill(us, them, -8, uint64(0x00FFFFFFFFFFFFFF)); moves |= p >>  8
    # E
    p = directional_fill(us, them,  1, uint64(0x7F7F7F7F7F7F7F7F)); moves |= p <<  1
    # W
    p = directional_fill(us, them, -1, uint64(0xFEFEFEFEFEFEFEFE)); moves |= p >>  1
    # NE
    p = directional_fill(us, them,  9, uint64(0x007F7F7F7F7F7F00)); moves |= p <<  9
    # NW
    p = directional_fill(us, them,  7, uint64(0x00FEFEFEFEFEFE00)); moves |= p <<  7
    # SE
    p = directional_fill(us, them, -7, uint64(0x7F7F7F7F7F7F7F00)); moves |= p >>  7
    # SW
    p = directional_fill(us, them, -9, uint64(0xFEFEFEFEFEFEFE00)); moves |= p >>  9

    return moves & empty
# jit_utils.py

from numba import njit, uint64

@njit("uint64(uint64, uint64)", cache=True, fastmath=True)  # type: ignore
def legal_moves_jit(us, them):
    """
    Return a 64-bit bitboard of legal moves for bitboards `us` and `them`.
    Implements the same 2D-scan logic as Board.legal_moves, but in nopython mode.
    """
    mask_all = uint64(0xFFFFFFFFFFFFFFFF)
    empty    = (~(us | them)) & mask_all
    moves_bb = uint64(0)

    # Directions N, NE, E, SE, S, SW, W, NW
    drs = (-1, -1,  0,  1, 1,  1,  0, -1)
    dcs = ( 0,  1,  1,  1, 0, -1, -1, -1)

    for idx in range(64):
        # board indices map to bit index (63 - idx)
        bidx = uint64(63 - idx)
        # only consider empty squares
        if ((empty >> bidx) & uint64(1)) == uint64(0):
            continue
        r = idx // 8
        c = idx % 8

        # scan each direction for bracketed run
        for k in range(8):
            dr = drs[k]; dc = dcs[k]
            rr = r + dr; cc = c + dc
            count = 0

            # run over opponent discs
            while 0 <= rr < 8 and 0 <= cc < 8:
                j   = rr * 8 + cc
                bit = uint64(1) << uint64(63 - j)  # type: ignore
                if (them & bit) != uint64(0):
                    count += 1
                    rr += dr; cc += dc
                    continue
                # if we saw ≥1 opponent and now see our disc, it's legal
                if count > 0 and (us & bit) != uint64(0):
                    moves_bb |= uint64(1) << uint64(idx)  # type: ignore
                break

    return moves_bb
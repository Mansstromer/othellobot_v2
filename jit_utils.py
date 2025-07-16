# jit_utils.py

from numba import njit, uint64

@njit("uint64(uint64, uint64)", cache=True, fastmath=True)  # type: ignore
def legal_moves_jit(us, them):
    # (This remains as your JIT‐scan stub, but is no longer wired in.)
    mask_all = uint64(0xFFFFFFFFFFFFFFFF)
    empty    = (~(us | them)) & mask_all
    moves_bb = uint64(0)
    drs = (-1,-1,0,1,1,1,0,-1)
    dcs = (0,1,1,1,0,-1,-1,-1)
    for idx in range(64):
        if ((empty >> uint64(idx)) & uint64(1)) == uint64(0):
            continue
        r = idx // 8; c = idx % 8
        for k in range(8):
            dr = drs[k]; dc = dcs[k]
            rr = r + dr; cc = c + dc; count = 0
            while 0 <= rr < 8 and 0 <= cc < 8:
                j = rr*8 + cc
                bit = uint64(1) << uint64(j)  # type: ignore
                if (them & bit) != uint64(0):
                    count += 1; rr += dr; cc += dc; continue
                if count > 0 and (us & bit) != uint64(0):
                    moves_bb |= uint64(1) << uint64(idx)  # type: ignore
                break
    return moves_bb
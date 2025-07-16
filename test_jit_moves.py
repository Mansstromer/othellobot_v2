import pytest, numpy as np
from board import Board
from jit_utils import legal_moves_jit

def jit_moves(b: Board, player: int):
    us   = np.uint64(b.black if player==1 else b.white)
    them = np.uint64(b.white if player==1 else b.black)
    bb = int(legal_moves_jit(us, them))
    res = []
    while bb:
        lsb = bb & -bb
        res.append(lsb.bit_length() - 1)
        bb ^= lsb
    return sorted(res)

@pytest.mark.parametrize("player", [1, -1])
def test_start_jit(player):
    b = Board.start_pos()
    assert jit_moves(b, player) == sorted(b.legal_moves(player))

@pytest.mark.parametrize("player", [1, -1])
def test_midgame_jit(player):
    b = Board.start_pos()
    # apply a few fixed moves to avoid randomness in tests
    for mv in [19, 26, 37, 44]:
        b.apply_move(mv, 1 if (b.to_flat_fen().count('X')+b.to_flat_fen().count('O'))%2==0 else -1)
    assert jit_moves(b, player) == sorted(b.legal_moves(player))
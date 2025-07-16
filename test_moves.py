# tests_moves.py

import pytest
import random
from board import Board
from moves_utils import get_moves

@pytest.mark.parametrize("player", [1, -1])
def test_start_pos_moves(player):
    b = Board.start_pos()
    assert sorted(get_moves(b, player)) == sorted(b.legal_moves(player))

@pytest.fixture
def midgame_board():
    b = Board.start_pos()
    player = 1
    for _ in range(6):
        mlist = b.legal_moves(player)
        if not mlist:
            player *= -1
            continue
        b.apply_move(random.choice(mlist), player)
        player *= -1
    return b

@pytest.mark.parametrize("player", [1, -1])
def test_midgame_moves(midgame_board, player):
    b = midgame_board
    assert sorted(get_moves(b, player)) == sorted(b.legal_moves(player))

if __name__ == "__main__":
    pytest.main([__file__])
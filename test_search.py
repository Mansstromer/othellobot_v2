import search
from board import Board


def test_final_eval_infinity():
    b_black = Board.from_flat_fen('X'*64)
    assert search.final_eval(b_black) == search.INF

    b_white = Board.from_flat_fen('O'*64)
    assert search.final_eval(b_white) == -search.INF

    half = 'X'*32 + 'O'*32
    b_tie = Board.from_flat_fen(half)
    assert search.final_eval(b_tie) == 0


def test_search_depth_actual_moves():
    # Position where black must pass and only one move is left
    fen = 'OOOOOOOOOOOOOOOOOOO.OOOOOO.XOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO'
    b = Board.from_flat_fen(fen)
    search.iterative_deepening(b, -1, time_limit=0.2)
    assert search.last_search_depth == 1

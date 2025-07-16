from board import Board
from eval_utils import evaluate
from engine import get_moves

def test_start_pos():
    b = Board.start_pos()
    assert len(get_moves(b,1)) == 4
    assert evaluate(b,1) == evaluate(b,-1)

if __name__ == "__main__":
    test_start_pos()
    print("All tests pass")
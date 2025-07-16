from board import Board
from moves_utils import get_moves
from eval_utils import evaluate

def test_start():
    b = Board.start_pos()
    assert len(get_moves(b,1)) == 4
    assert evaluate(b,1) == evaluate(b,-1)

if __name__ == '__main__':
    test_start()
    print("All tests pass")
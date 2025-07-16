from board import Board
from moves_utils import get_moves
from engine import choose_move, TimeManager, index_to_coord
import io, sys

def test_book_print():
    # Build a minimal draft book mapping the start position to its first move
    start = Board.start_pos()
    fen0 = start.to_flat_fen()
    mv0 = get_moves(start, 1)[0]
    book = {fen0: mv0}

    # Capture stdout during choose_move
    timer = TimeManager()
    buf = io.StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdout = buf
        chosen = choose_move(start, player=1, ply=0, timer=timer, book=book)
    finally:
        sys.stdout = old_stdout

    output = buf.getvalue()
    coord = index_to_coord(chosen)

    # Check returned move matches the book and printed message
    assert chosen == mv0, f"Expected move {mv0} from book, got {chosen}"
    assert f"[Book] Ply 0 move {coord}" in output, (
        f"Expected '[Book] Ply 0 move {coord}' in output, got: {output!r}" )
    print("Book test passed")

if __name__ == '__main__':
    test_book_print()
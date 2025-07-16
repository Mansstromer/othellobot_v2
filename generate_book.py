# generate_book.py

import json
from board import Board
from moves_utils import get_moves
from search import iterative_deepening

def build_draft_book(time_per_move=0.1):
    """
    Plays Black’s first move and White’s reply using a short search,
    then records both positions→move mappings.
    """
    book = {}
    start = Board.start_pos()

    # Black’s 1st move
    for mv in get_moves(start, 1):
        fen1 = start.to_flat_fen()
        book[fen1] = mv

        # White’s reply
        start.apply_move(mv, 1)
        reply = iterative_deepening(start, -1, time_limit=time_per_move)
        fen2 = start.to_flat_fen()
        book[fen2] = reply

        start.undo()  # back to start for next Black mv

    return book

if __name__ == "__main__":
    print("Building draft opening book…")
    book = build_draft_book(time_per_move=0.1)
    with open("book.json", "w") as f:
        json.dump(book, f, indent=2)
    print(f"Wrote {len(book)} entries to book.json")
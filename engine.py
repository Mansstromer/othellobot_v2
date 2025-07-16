# engine.py
"""Othello engine front end

Performance accelerations used when running this file:

* **Bitboards** – board state is kept as two 64‑bit integers which makes
  flipping and move lookups fast.
* **Numba JIT move generation** – when ``USE_JIT`` is enabled the legal move
  generator is compiled with Numba (``legal_moves_jit``).  The compiled version
  runs in ``nopython`` mode with ``fastmath`` and results are cached so the
  costly compilation happens only once.
* **Iterative deepening negamax search** implemented in :mod:`search`.  The
  search uses alpha–beta pruning, a transposition table, principal variation
  (PV) move ordering and aspiration windows.  For deeper levels the root moves
  are searched in parallel using ``ProcessPoolExecutor``.
* **Opening book** – early moves can be played instantly from ``book.json``.
* **Time management** – ``TimeManager`` slices the total allotted time per move
  so the engine does not exceed the game clock.

Instrumentation counters for nodes, transposition‑table hits and cutoffs are
recorded for every move and printed so that the performance of the JIT and
non‑JIT modes can be compared.
"""

import time
import os
import json
from board import Board
from eval_utils import evaluate
from search import iterative_deepening, last_search_depth
import search  # for the last_search_depth variable

# Toggle between JIT-accelerated and pure-Python move generation
USE_JIT = True  # set to False to use Python fallback

if USE_JIT:
    import numpy as np
    from jit_utils import legal_moves_jit

    def get_moves(board: Board, player: int) -> list[int]:
        """
        JIT-powered move generator wrapping `legal_moves_jit`.
        """
        us = np.uint64(board.black if player == 1 else board.white)
        them = np.uint64(board.white if player == 1 else board.black)
        bb = legal_moves_jit(us, them)
        bbi = int(bb)  # type: ignore
        moves = []
        while bbi:
            lsb = bbi & -bbi
            moves.append(lsb.bit_length() - 1)
            bbi ^= lsb
        return moves
else:
    from moves_utils import get_moves  # pure-Python fallback

TOTAL_TIME = 600.0   # 10 minutes per game, in seconds
SAFETY     = 0.8    # use only 95% of each slice

class TimeManager:
    def __init__(self):
        self.remaining = TOTAL_TIME

    def slice(self, ply: int) -> float:
        moves_left = max(1, 60 - ply)
        base = self.remaining / moves_left
        return max(1.0, min(base, 40.0)) * SAFETY

    def spend(self, used: float) -> None:
        self.remaining = max(0.0, self.remaining - used)

def load_opening_book(path: str = "book_expanded.json") -> dict[str,int]:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
        return {k: int(v) for k, v in data.items()}
    return {}

def index_to_coord(idx: int) -> str:
    col = idx % 8
    row = idx // 8
    return f"{chr(ord('A') + col)}{row + 1}"

def coord_to_index(coord: str) -> int:
    c = coord[0].upper()
    r = int(coord[1])
    col = ord(c) - ord('A')
    row = r - 1
    return row * 8 + col

def print_board(board: Board, moves: list[int] | None = None) -> None:
    """Print the board with column letters and row numbers; highlight legal moves with '*'"""
    fen = board.to_flat_fen()
    symbols = {'X': 'X', 'O': '0', '.': '.'}
    move_set = set(moves) if moves else set()
    print("  " + " ".join(chr(ord('A') + i) for i in range(8)))
    for r in range(8):
        row_cells = []
        for c in range(8):
            idx = r * 8 + c
            if idx in move_set:
                cell = '*'
            else:
                ch = fen[idx]
                cell = symbols[ch]
            row_cells.append(cell)
        print(f"{r + 1} " + " ".join(row_cells))

def choose_move(board: Board, player: int, ply: int,
                timer: TimeManager, book: dict[str,int]) -> int:
    fen = board.to_flat_fen()
    moves = get_moves(board, player)
    if fen in book:
        mv = book[fen]
        if mv in moves:
            coord = index_to_coord(mv)
            print(f"[Book] Ply {ply} move {coord}")
            return mv
        else:
            bad = index_to_coord(mv)
            print(f"[Book] Illegal move {bad} ignored")

    think = timer.slice(ply)
    print(f"[Ply {ply}] Bot is thinking... allocated {think:.1f}bs")
    t0 = time.monotonic()
    mv = iterative_deepening(board, player, time_limit=think)
    used = time.monotonic() - t0
    timer.spend(used)
    depth = search.last_search_depth
    nodes = search.nodes_searched
    tt = search.tt_hits
    cuts = search.cutoffs
    print(
        f"[Ply {ply}] Think {think:.1f}s, used {used:.2f}s, remain {timer.remaining:.2f}s, depth {depth}, nodes {nodes}, TT {tt}, cutoffs {cuts}"
    )
    return mv

def main():
    side = input("Which side should the bot play? (b=Black, w=White, both=Both) > ").strip().lower()
    bot_black = side in ('b', 'both')
    bot_white = side in ('w', 'both')

    book = load_opening_book()
    timer = TimeManager()
    board = Board.start_pos()
    ply = 0
    current_player = 1  # 1 == Black, -1 == White
    pass_count = 0

    while True:
        print("\nCurrent board:")
        is_bot = (current_player == 1 and bot_black) or (current_player == -1 and bot_white)
        moves = get_moves(board, current_player)

        if not is_bot and moves:
            print_board(board, moves)
        else:
            print_board(board)
        print(f"Time remaining: {timer.remaining:.1f}s")

        if moves:
            pass_count = 0
            if is_bot:
                mv = choose_move(board, current_player, ply, timer, book)
                coord = index_to_coord(mv)
                print(f"Bot plays {'Black' if current_player==1 else 'White'}: {coord}")
                board.apply_move(mv, current_player)
                # flip turn
                current_player = -current_player
                ply += 1
            else:
                coords = [index_to_coord(m) for m in moves]
                while True:
                    inp = input(f"Your move {coords} > ").strip().lower()
                    if inp == 'stop':
                        print("Game stopped by user."); return
                    if inp == 'undo':
                        if ply > 0:
                            board.undo()
                            ply  -= 1
                            # rewind turn as well
                            current_player = -current_player
                            print("Last move undone. Board is now:")
                            print_board(board)
                        else:
                            print("Nothing to undo.")
                        # re-prompt until a real move
                        continue
                    if inp.upper() in coords:
                        mv = coord_to_index(inp)
                        break
                    print(f"Invalid input. Enter one of {coords}, 'undo', or 'stop'.")
                print(f"You play {'Black' if current_player==1 else 'White'}: {inp.upper()}")
                board.apply_move(mv, current_player)
                current_player = -current_player
                ply += 1

        else:
            # pass
            pass_count += 1
            print(f"{'Bot' if is_bot else 'You'} pass.")
            current_player = -current_player
            ply += 1
            if pass_count >= 2:
                print("Two passes in a row: game over.")
                break


        # check for time exhaustion
        if timer.remaining <= 0:
            print("Bot clock exhausted! Bot loses on time.")
            break

    # game over: tally and report final score
    black_count = bin(board.black).count('1')
    white_count = bin(board.white).count('1')
    print("Final board:")
    print_board(board)
    print(f"Score — Black: {black_count}, White: {white_count}")
    if black_count > white_count:
        print("Black wins!")
    elif white_count > black_count:
        print("White wins!")
    else:
        print("It's a tie!")

if __name__ == '__main__':
    main()

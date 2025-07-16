# engine.py

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
SAFETY     = 0.95    # use only 95% of each slice

class TimeManager:
    def __init__(self):
        self.remaining = TOTAL_TIME

    def slice(self, ply: int) -> float:
        moves_left = max(1, 60 - ply)
        base = self.remaining / moves_left
        return max(1.0, min(base, 40.0)) * SAFETY

    def spend(self, used: float) -> None:
        self.remaining = max(0.0, self.remaining - used)

def load_opening_book(path: str = "book.json") -> dict[str,int]:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
        return {k: int(v) for k, v in data.items()}
    return {}

def index_to_coord(idx: int) -> str:
    col = idx % 8
    row = idx // 8
    return f"{chr(ord('A') + col)}{8 - row}"

def coord_to_index(coord: str) -> int:
    c = coord[0].upper()
    r = int(coord[1])
    col = ord(c) - ord('A')
    row = 8 - r
    return row * 8 + col

def print_board(board: Board, moves: list[int] | None = None) -> None:
    """Print the board with column letters and row numbers; highlight legal moves with '*'"""
    fen = board.to_flat_fen()
    symbols = {'X': 'B', 'O': 'W', '.': '.'}
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
        print(f"{8 - r} " + " ".join(row_cells))

def choose_move(board: Board, player: int, ply: int,
                timer: TimeManager, book: dict[str,int]) -> int:
    fen = board.to_flat_fen()
    if fen in book:
        mv = book[fen]
        coord = index_to_coord(mv)
        print(f"[Book] Ply {ply} move {coord}")
        return mv

    think = timer.slice(ply)
    print(f"[Ply {ply}] Bot is thinking... allocated {think:.1f}s")
    t0 = time.monotonic()
    mv = iterative_deepening(board, player, time_limit=think)
    used = time.monotonic() - t0
    timer.spend(used)
    depth = search.last_search_depth
    print(f"[Ply {ply}] Think {think:.1f}s, used {used:.2f}s, remain {timer.remaining:.2f}s, depth {depth}")
    return mv

def main():
    side = input("Which side should the bot play? (b=Black, w=White, both=Both) > ").strip().lower()
    bot_black = side in ('b', 'both')
    bot_white = side in ('w', 'both')

    book = load_opening_book()
    timer = TimeManager()
    board = Board.start_pos()
    ply = 0

    while True:
        print("\nCurrent board:")
        player = 1 if ply % 2 == 0 else -1
        is_bot = (player == 1 and bot_black) or (player == -1 and bot_white)
        moves = get_moves(board, player)
        if not is_bot and moves:
            print_board(board, moves)
        else:
            print_board(board)
        print(f"Time remaining: {timer.remaining:.1f}s")

        if moves:
            if is_bot:
                mv = choose_move(board, player, ply, timer, book)
                coord = index_to_coord(mv)
                print(f"Bot plays {'Black' if player==1 else 'White'}: {coord}")
                board.apply_move(mv, player)
                ply += 1
            else:
                coords = [index_to_coord(m) for m in moves]
                while True:
                    inp = input(f"Your move {coords} > ").strip()
                    if inp.lower() == 'stop':
                        print("Game stopped by user."); return
                    if inp.lower() == 'undo':
                        if ply > 0:
                            board.undo(); ply -= 1
                            print("Last move undone. Board is now:"); print_board(board)
                        else:
                            print("Nothing to undo.")
                        continue
                    if inp.upper() in coords:
                        mv = coord_to_index(inp); break
                    print(f"Invalid input. Enter one of {coords}, 'undo', or 'stop'.")
                print(f"You play {'Black' if player==1 else 'White'}: {inp.upper()}")
                board.apply_move(mv, player)
                ply += 1
        else:
            print(f"{'Bot' if is_bot else 'You'} pass.")

        if not (get_moves(board,1) or get_moves(board,-1)):
            print("Game over."); break
        if timer.remaining <= 0:
            print("Bot clock exhausted! Bot loses on time."); break

    print("Final board:"); print_board(board)

if __name__ == '__main__':
    main()
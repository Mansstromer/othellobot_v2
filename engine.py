# engine.py

import time
import numpy as np
from board import Board
from moves_utils import get_moves
from eval_utils import evaluate
from search import iterative_deepening

TOTAL_TIME = 600.0   # total thinking time per game (seconds)
SAFETY     = 0.95    # use only 95% of allocated slice to avoid overruns

class TimeManager:
    def __init__(self):
        self.remaining = TOTAL_TIME

    def budget(self, ply: int) -> float:
        """
        Estimate a per‐move slice:
          moves left ≈ max(1, 60 – ply)
          slice = remaining / moves_left, clamped [1, 40] seconds
        """
        moves_left = max(1, 60 - ply)
        slice_ = self.remaining / moves_left
        return min(max(slice_, 1.0), 40.0)

    def deduct(self, used: float):
        self.remaining = max(0.0, self.remaining - used)

def get_moves(board: Board, player: int) -> list[int]:
    us   = np.uint64(board.black   if player == 1 else board.white)
    them = np.uint64(board.white   if player == 1 else board.black)
    moves_bb = legal_moves_jit(us, them)
    moves = []
    bb = int(moves_bb)
    while bb:
        lsb = bb & -bb
        idx = lsb.bit_length() - 1
        moves.append(idx)
        bb ^= lsb
    return moves

def evaluate_board(board: Board, player: int) -> int:
    return evaluate(board, player)

def choose_move(board: Board, player: int, ply: int, timer: TimeManager) -> int:
    """
    Pick a move via iterative deepening within the time budget.
    `ply` is the move‐count so far (0 at start), used to estimate moves_left.
    """
    slice_ = timer.budget(ply) * SAFETY
    start = time.monotonic()
    move = iterative_deepening(board, player, time_limit=slice_)
    used = time.monotonic() - start
    timer.deduct(used)
    print(f"[Ply {ply}] Used {used:.2f}s, Remains {timer.remaining:.2f}s")
    return move

def main():
    timer = TimeManager()
    ply = 0
    board = Board.start_pos()

    while True:
        print("\nCurrent board:")
        print(board, "\n")
        print(f"Time left: {timer.remaining:.1f}s")
        # Our bot is always Black (1)
        move = choose_move(board, player=1, ply=ply, timer=timer)
        print(f"Bot plays: {move}")
        board.apply_move(move, 1)
        ply += 1

        # Check for opponent pass
        opp_moves = get_moves(board, -1)
        if opp_moves:
            inp = input("Your move (0–63): ")
            mv = int(inp)
            board.apply_move(mv, -1)
            ply += 1
        else:
            print("Opponent passes.")
            # Opponent pass: skip their turn
        if timer.remaining <= 0:
            print("Clock exhausted!")
            break
        if not (get_moves(board,1) or get_moves(board,-1)):
            print("Game over.")
            break

if __name__ == "__main__":
    main()
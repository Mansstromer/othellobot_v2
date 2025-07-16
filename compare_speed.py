import time
import random
from typing import List, Tuple

from board import Board
import search


def generate_positions(count: int = 5, moves: int = 6) -> List[Board]:
    """Generate random midgame positions by playing random legal moves."""
    boards = []
    for _ in range(count):
        b = Board.start_pos()
        player = 1
        for __ in range(moves):
            mlist = b.legal_moves(player)
            if not mlist:
                player *= -1
                continue
            mv = random.choice(mlist)
            b.apply_move(mv, player)
            player *= -1
        boards.append(b)
    return boards


def run_searches(time_per: float = 0.5, count: int = 5, moves: int = 6) -> List[Tuple[float, float]]:
    """Run JIT and pure Python searches on random positions and return timings."""
    positions = generate_positions(count=count, moves=moves)
    results = []
    for b in positions:
        # JIT-based search using moves_utils.get_moves
        search.trans_table.clear()
        start = time.monotonic()
        search.iterative_deepening(b, 1, time_limit=time_per)
        jit_time = time.monotonic() - start

        # Pure Python search using Board.legal_moves
        search.trans_table.clear()
        orig_get_moves = search.get_moves
        try:
            def py_moves(board: Board, player: int) -> List[int]:
                return board.legal_moves(player)
            search.get_moves = py_moves
            start = time.monotonic()
            search.iterative_deepening(b, 1, time_limit=time_per)
            py_time = time.monotonic() - start
        finally:
            search.get_moves = orig_get_moves

        results.append((jit_time, py_time))
    return results


def main() -> None:
    results = run_searches(time_per=0.5, count=5, moves=6)
    for i, (jit_t, py_t) in enumerate(results):
        print(f"Position {i}: JIT {jit_t:.3f}s | Python {py_t:.3f}s")
    avg_jit = sum(j for j, _ in results) / len(results)
    avg_py = sum(p for _, p in results) / len(results)
    print(f"Average JIT time: {avg_jit:.3f}s")
    print(f"Average Python time: {avg_py:.3f}s")


if __name__ == "__main__":
    main()

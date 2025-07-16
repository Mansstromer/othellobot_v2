# benchmark_search.py

import time
import random
import pandas as pd
from board import Board
from search import iterative_deepening


def generate_positions(count: int = 10, moves: int = 6) -> list[Board]:
    """
    Generate `count` random midgame positions by playing `moves` random legal moves.
    Returns a list of Board instances.
    """
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


def benchmark(time_per_search: float = 0.5, count: int = 10, moves: int = 6) -> pd.DataFrame:
    """
    Run `iterative_deepening` on random positions and record elapsed times.
    Returns a pandas DataFrame with columns: position, elapsed_s.
    """
    positions = generate_positions(count=count, moves=moves)
    results = []
    for i, b in enumerate(positions):
        t0 = time.monotonic()
        _ = iterative_deepening(b, 1, time_limit=time_per_search)
        elapsed = time.monotonic() - t0
        results.append({"position": i, "elapsed_s": elapsed})
    return pd.DataFrame(results)


if __name__ == "__main__":
    df = benchmark(time_per_search=0.5, count=10, moves=6)
    print(df.to_string(index=False))
    print(f"\nAverage time: {df['elapsed_s'].mean():.3f}s")
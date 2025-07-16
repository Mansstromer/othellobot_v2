import time
import random
from board import Board
from moves_utils import get_moves


def random_boards(count: int = 5, moves: int = 6) -> list[Board]:
    """Generate random midgame boards."""
    boards: list[Board] = []
    for _ in range(count):
        b = Board.start_pos()
        player = 1
        for __ in range(moves):
            mlist = b.legal_moves(player)
            if not mlist:
                player *= -1
                continue
            b.apply_move(random.choice(mlist), player)
            player *= -1
        boards.append(b)
    return boards


def measure(board: Board, iterations: int = 50000) -> tuple[float, float]:
    """Return (jit_time, python_time) for running legal move generation."""
    # warm-up numba compilation
    get_moves(board, 1)
    get_moves(board, -1)
    start = time.perf_counter()
    for _ in range(iterations):
        get_moves(board, 1)
        get_moves(board, -1)
    jit_time = time.perf_counter() - start

    # Python implementation
    board.legal_moves(1)
    board.legal_moves(-1)
    start = time.perf_counter()
    for _ in range(iterations):
        board.legal_moves(1)
        board.legal_moves(-1)
    py_time = time.perf_counter() - start
    return jit_time, py_time


def main() -> None:
    boards = random_boards(count=5, moves=6)
    jit_total = 0.0
    py_total = 0.0
    for i, b in enumerate(boards):
        jt, pt = measure(b)
        jit_total += jt
        py_total += pt
        print(f"Position {i}: JIT {jt:.3f}s | Python {pt:.3f}s")
    print(f"Average JIT time: {jit_total/len(boards):.3f}s")
    print(f"Average Python time: {py_total/len(boards):.3f}s")


if __name__ == "__main__":
    main()
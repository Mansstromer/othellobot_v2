# Othello Bot v2

A high-performance, bitboard-based Othello (Reversi) engine in Python, accelerated with Numba JIT and parallel root‐search. Plays up to 10 minutes per game, supports opening books, undo, and configurable move‐generation backends.

---

## 🚀 Features

- **Bitboard core** (`board.py`) for ultra‐fast state updates  
- **Negamax + α-β pruning** with:
  - Iterative deepening
  - Principal-variation move ordering
  - Aspiration windows
  - Transposition table
  - (Optional) Killer-move heuristic
- **Numba-JIT move generator** (`jit_utils.py`) —— ~10× faster than pure-Python  
- **Parallel root search** (via `ProcessPoolExecutor`) to leverage all CPU cores  
- **Time management** (`TimeManager`) with safety margin  
- **Opening book** support (plies 0–3 from `book.json`)  
- **CLI** (`engine.py`) with human vs. bot, undo, stop, and board display  
- **Test suite** (`test_moves.py`, `tests_jit_moves.py`) ensuring correctness  
- **Benchmark scripts** (`compare_speed.py`, `benchmark_movegen.py`) for profiling  

---

## 📦 Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/YOUR_USERNAME/othellobot_v2.git
   cd othellobot_v2

# search.py

import time
from typing import NamedTuple
from board import Board
from engine import get_moves
from eval_utils import evaluate

INF = 10**9

class TTEntry(NamedTuple):
    depth: int       # search depth of stored entry
    flag: str        # 'EXACT', 'LOWER', or 'UPPER'
    value: int       # score value from this position

# Simple transposition table
transposition_table: dict[tuple[int,int,int], TTEntry] = {}


def is_terminal(board: Board) -> bool:
    """
    True if neither side has any moves (game over).
    """
    return not get_moves(board, 1) and not get_moves(board, -1)


def final_evaluate(board: Board) -> int:
    """
    Final evaluation: difference in disc counts.
    """
    b_count = board.to_flat_fen().count('X')
    w_count = board.to_flat_fen().count('O')
    return b_count - w_count


def negamax(board: Board, player: int, depth: int, alpha: int, beta: int) -> int:
    """
    Negamax with alpha-beta pruning and transposition table.
    `player` is +1 for black, -1 for white.
    Returns the score from `player`'s POV.
    """
    # TT lookup
    key = (board.black, board.white, player)
    entry = transposition_table.get(key)
    if entry and entry.depth >= depth:
        if entry.flag == 'EXACT':
            return entry.value
        elif entry.flag == 'LOWER':
            alpha = max(alpha, entry.value)
        elif entry.flag == 'UPPER':
            beta = min(beta, entry.value)
        if alpha >= beta:
            return entry.value

    # Terminal or depth==0
    if depth == 0 or is_terminal(board):
        val = player * (final_evaluate(board) if is_terminal(board) else evaluate(board, player))
        return val

    moves = get_moves(board, player)
    # Pass logic
    if not moves:
        if not get_moves(board, -player):
            return player * final_evaluate(board)
        return -negamax(board, -player, depth, -beta, -alpha)

    best_value = -INF
    original_alpha = alpha

    for mv in moves:
        board.apply_move(mv, player)
        score = -negamax(board, -player, depth-1, -beta, -alpha)
        board.undo()

        if score > best_value:
            best_value = score
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    # TT store
    if best_value <= original_alpha:
        flag = 'UPPER'
    elif best_value >= beta:
        flag = 'LOWER'
    else:
        flag = 'EXACT'
    transposition_table[key] = TTEntry(depth, flag, best_value)

    return best_value


def iterative_deepening(root_board: Board, player: int, time_limit: float) -> int:
    """
    Iterative deepening over negamax to select best move within time_limit (seconds).
    Always returns an int move.
    """
    start = time.time()
    # Initialize best_move with first legal or 0
    initial_moves = get_moves(root_board, player)
    if not initial_moves:
        return 0  # no legal moves
    best_move = initial_moves[0]
    depth = 1

    while True:
        if time.time() - start > time_limit:
            break
        moves = get_moves(root_board, player)
        if not moves:
            break
        current_best = best_move
        alpha = -INF
        beta = INF
        for mv in moves:
            if time.time() - start > time_limit:
                break
            root_board.apply_move(mv, player)
            score = -negamax(root_board, -player, depth-1, -beta, -alpha)
            root_board.undo()
            if score > alpha:
                alpha = score
                current_best = mv
        best_move = current_best
        depth += 1
    return best_move


# Example quick test
if __name__ == '__main__':
    board = Board.start_pos()
    move = iterative_deepening(board, player=1, time_limit=1.0)
    print('Best move (1s search):', move)

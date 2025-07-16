import time
import concurrent.futures
from typing import NamedTuple
from board import Board
from moves_utils import get_moves
from eval_utils import evaluate

INF = 10**9

class TTEntry(NamedTuple):
    depth: int
    flag: str   # 'EXACT', 'LOWER', or 'UPPER'
    value: int

# Transposition table using a dict
trans_table: dict[tuple[int,int,int], TTEntry] = {}

def tt_lookup(key, depth, alpha, beta):
    entry = trans_table.get(key)
    if entry and entry.depth >= depth:
        if entry.flag == 'EXACT':
            return entry.value, alpha, beta
        if entry.flag == 'LOWER':
            alpha = max(alpha, entry.value)
        if entry.flag == 'UPPER':
            beta  = min(beta,  entry.value)
        if alpha >= beta:
            return entry.value, alpha, beta
    return None, alpha, beta

def tt_store(key, depth, value, alpha, beta, orig_alpha):
    if value <= orig_alpha:
        flag = 'UPPER'
    elif value >= beta:
        flag = 'LOWER'
    else:
        flag = 'EXACT'
    trans_table[key] = TTEntry(depth, flag, value)


def is_terminal(b: Board) -> bool:
    return not get_moves(b, 1) and not get_moves(b, -1)


def final_eval(b: Board) -> int:
    fen = b.to_flat_fen()
    return fen.count('X') - fen.count('O')


def negamax(b: Board, player: int, depth: int, alpha: int, beta: int) -> int:
    key = (b.black, b.white, player)
    orig_alpha = alpha
    val, alpha, beta = tt_lookup(key, depth, alpha, beta)
    if val is not None:
        return val

    if depth == 0 or is_terminal(b):
        return player * (final_eval(b) if is_terminal(b) else evaluate(b, player))

    moves = get_moves(b, player)
    if not moves:
        if not get_moves(b, -player):
            return player * final_eval(b)
        return -negamax(b, -player, depth, -beta, -alpha)

    best_score = -INF
    for mv in moves:
        b.apply_move(mv, player)
        score = -negamax(b, -player, depth-1, -beta, alpha)
        b.undo()
        if score > best_score:
            best_score = score
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    tt_store(key, depth, best_score, alpha, beta, orig_alpha)
    return best_score


def _root_worker(args):
    black, white, player, mv, depth = args
    b = Board(black, white)
    b.apply_move(mv, player)
    score = -negamax(b, -player, depth, -INF, INF)
    return mv, score


def iterative_deepening(root: Board, player: int, time_limit: float) -> int:
    start = time.time()
    moves = get_moves(root, player)
    if not moves:
        return 0
    best_move = moves[0]
    depth = 1

    while True:
        elapsed = time.time() - start
        if elapsed >= time_limit:
            break
        current_best = best_move

        # parallel root search at deeper plies
        if depth >= 3:
            best_score = -INF
            args = [(root.black, root.white, player, mv, depth-1) for mv in moves]
            time_left = time_limit - elapsed
            with concurrent.futures.ProcessPoolExecutor() as ex:
                futures = {ex.submit(_root_worker, arg): arg[3] for arg in args}
                try:
                    for fut in concurrent.futures.as_completed(futures, timeout=time_left):
                        mv, score = fut.result()
                        if score > best_score:
                            best_score = score
                            current_best = mv
                except concurrent.futures.TimeoutError:
                    # time ran out; proceed with best found so far
                    pass
            best_move = current_best
        else:
            alpha = -INF
            for mv in moves:
                elapsed = time.time() - start
                if elapsed >= time_limit:
                    break
                root.apply_move(mv, player)
                score = -negamax(root, -player, depth-1, -INF, INF)
                root.undo()
                if score > alpha:
                    alpha = score
                    current_best = mv
            best_move = current_best

        depth += 1
    return best_move


if __name__ == '__main__':
    b = Board.start_pos()
    print("Best move (1s search):", iterative_deepening(b, 1, 1.0))
# search.py

import time
import concurrent.futures
from typing import NamedTuple
from board import Board
from moves_utils import get_moves
from eval_utils import evaluate


# Depth reached on the most recent search
last_search_depth = 0
# Track the deepest ply seen for the current iteration
max_depth_reached = 0
# instrumentation counters for performance statistics
nodes_searched = 0
tt_hits = 0
cutoffs = 0

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
        global tt_hits
        tt_hits += 1
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
    """Return \+INF or \-INF depending on who wins the finished board."""
    black = bin(b.black).count("1")
    white = bin(b.white).count("1")
    if black > white:
        return INF
    if white > black:
        return -INF
    return 0

def score(b: Board, player: int) -> int:
    """Evaluation from ``player``'s perspective with infinite endgame values."""
    return final_eval(b) * player if is_terminal(b) else evaluate(b, player)

def negamax(b: Board, player: int, depth: int, alpha: int, beta: int, ply: int = 0) -> int:
    global nodes_searched, max_depth_reached
    nodes_searched += 1
    key = (b.black, b.white, player)
    orig_alpha = alpha
    val, alpha, beta = tt_lookup(key, depth, alpha, beta)
    if val is not None:
        return val

    if depth == 0 or is_terminal(b):
        if ply > max_depth_reached:
            max_depth_reached = ply
        return player * (final_eval(b) if is_terminal(b) else evaluate(b, player))

    moves = get_moves(b, player)
    if not moves:
        # pass or game end
        if not get_moves(b, -player):
            if ply > max_depth_reached:
                max_depth_reached = ply
            return player * final_eval(b)
        return -negamax(b, -player, depth, -beta, -alpha, ply + 1)

    best_score = -INF
    for mv in moves:
        b.apply_move(mv, player)
        score = -negamax(b, -player, depth-1, -beta, alpha, ply + 1)
        b.undo()
        if score > best_score:
            best_score = score
        alpha = max(alpha, score)
        if alpha >= beta:
            global cutoffs
            cutoffs += 1
            break

    tt_store(key, depth, best_score, alpha, beta, orig_alpha)
    return best_score

def _root_worker(args):
    black, white, player, mv, depth = args
    b = Board(black, white)
    b.apply_move(mv, player)
    # local counters
    global nodes_searched, tt_hits, cutoffs, max_depth_reached, last_search_depth
    nodes_searched = 0
    tt_hits = 0
    cutoffs = 0
    max_depth_reached = 0
    last_search_depth = 0
    score = -negamax(b, -player, depth, -INF, INF, 1)
    return mv, score, nodes_searched, tt_hits, cutoffs, max_depth_reached

def iterative_deepening(root: Board, player: int, time_limit: float) -> int:
    """
    Iterative-deepening negamax with alpha-beta, transposition table,
    principal-variation move ordering, aspiration windows, exact endgame,
    and a strict monotonic deadline.
    """
    start_time = time.monotonic()
    deadline = start_time + time_limit
    global nodes_searched, tt_hits, cutoffs, max_depth_reached, last_search_depth
    nodes_searched = 0
    tt_hits = 0
    cutoffs = 0
    max_depth_reached = 0
    last_search_depth = 0

    moves = get_moves(root, player)
    if not moves:
        return 0

    best_move = moves[0]
    prev_score = 0
    depth = 1

    while True:
        now = time.monotonic()
        if now >= deadline or is_terminal(root):
            break

        max_depth_reached = 0

        # PV move ordering: try last best_move first
        if depth > 1 and best_move in moves:
            moves = [best_move] + [m for m in moves if m != best_move]

        # Set up aspiration window
        if depth > 1:
            delta = 50  # centipawns
            alpha = prev_score - delta
            beta  = prev_score + delta
            alpha = max(-INF, alpha)
            beta  = min(INF, beta)
        else:
            alpha = -INF
            beta  = INF

        current_best = best_move

        # Shallow: serial search
        if depth < 3:
            best_score = -INF
            for mv in moves:
                if time.monotonic() >= deadline:
                    break
                root.apply_move(mv, player)
                score = -negamax(root, -player, depth-1, -beta, -alpha, 1)
                root.undo()
                if score > best_score:
                    best_score = score
                    current_best = mv
                alpha = max(alpha, score)
                # aspiration fail: full re-search
                if alpha >= beta:
                    best_score = -negamax(root, player, depth, -INF, INF, 0)
                    current_best = mv
                    break
            prev_score = best_score
            best_move = current_best
            last_search_depth = max_depth_reached
            if max_depth_reached < depth:
                break
            depth += 1
            continue

        # Deep: parallel root search
        time_left = deadline - time.monotonic()
        if time_left <= 0:
            break
        best_score = -INF
        args = [(root.black, root.white, player, mv, depth-1) for mv in moves]
        with concurrent.futures.ProcessPoolExecutor() as ex:
            futures = {ex.submit(_root_worker, arg): arg[3] for arg in args}
            try:
                for fut in concurrent.futures.as_completed(futures, timeout=time_left):
                    mv, score, n, tt, co, d = fut.result()
                    nodes_searched += n
                    tt_hits += tt
                    cutoffs += co
                    if d > max_depth_reached:
                        max_depth_reached = d
                    if score > best_score:
                        best_score = score
                        current_best = mv
            except concurrent.futures.TimeoutError:
                break
        best_move = current_best
        last_search_depth = max_depth_reached
        if max_depth_reached < depth:
            break
        depth += 1

    return best_move

if __name__ == '__main__':
    b = Board.start_pos()
    print("Best move (1s search):", iterative_deepening(b, 1, 1.0))

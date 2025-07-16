import time
from typing import NamedTuple
from board import Board
from moves_utils import get_moves
from eval_utils import evaluate

INF = 10**9

class TTEntry(NamedTuple):
    depth: int
    flag: str   # 'EXACT' / 'LOWER' / 'UPPER'
    value: int

trans_table: dict[tuple[int,int,int], TTEntry] = {}

def is_terminal(b: Board) -> bool:
    return not get_moves(b,1) and not get_moves(b,-1)

def final_eval(b: Board) -> int:
    fen = b.to_flat_fen()
    return fen.count('X') - fen.count('O')

def negamax(b: Board, player: int, depth: int, alpha: int, beta: int) -> int:
    key = (b.black, b.white, player)
    entry = trans_table.get(key)
    if entry and entry.depth >= depth:
        if entry.flag == 'EXACT': return entry.value
        if entry.flag == 'LOWER': alpha = max(alpha, entry.value)
        if entry.flag == 'UPPER': beta  = min(beta,  entry.value)
        if alpha >= beta: return entry.value

    if depth == 0 or is_terminal(b):
        return player * (final_eval(b) if is_terminal(b) else evaluate(b, player))

    moves = get_moves(b, player)
    if not moves:
        if not get_moves(b, -player):
            return player * final_eval(b)
        return -negamax(b, -player, depth, -beta, -alpha)

    best = -INF
    orig_alpha = alpha
    for mv in moves:
        b.apply_move(mv, player)
        score = -negamax(b, -player, depth-1, -beta, -alpha)
        b.undo()
        best = max(best, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    flag = 'EXACT'
    if best <= orig_alpha: flag = 'UPPER'
    elif best >= beta:     flag = 'LOWER'
    trans_table[key] = TTEntry(depth, flag, best)
    return best

def iterative_deepening(root: Board, player: int, time_limit: float) -> int:
    start = time.time()
    moves = get_moves(root, player)
    if not moves: return 0
    best_move = moves[0]
    depth = 1
    while time.time() - start < time_limit:
        alpha = -INF
        for mv in moves:
            if time.time() - start >= time_limit: break
            root.apply_move(mv, player)
            score = -negamax(root, -player, depth-1, -INF, INF)
            root.undo()
            if score > alpha:
                alpha = score
                best_move = mv
        depth += 1
    return best_move

if __name__ == '__main__':
    b = Board.start_pos()
    print("Best move at depth-increment for 1s:", iterative_deepening(b,1,1.0))
# eval_utils.py

# Positional weight table (row-major, top-left first)
SQUARE_WEIGHTS = [
     20, -3, 11,  8,  8, 11, -3, 20,
     -3, -7, -4,  1,  1, -4, -7, -3,
     11, -4,  2,  2,  2,  2, -4, 11,
      8,  1,  2, -3, -3,  2,  1,  8,
      8,  1,  2, -3, -3,  2,  1,  8,
     11, -4,  2,  2,  2,  2, -4, 11,
     -3, -7, -4,  1,  1, -4, -7, -3,
     20, -3, 11,  8,  8, 11, -3, 20,
]

def evaluate(board, player):
    """
    Static evaluation of `board` from `player`’s POV.
    Combines:
      - square weights,
      - mobility (your moves – opp’s moves),
      - corner occupancy.
    """
    # Disc counts & bitboards
    my_bb   = board.black if player == 1 else board.white
    opp_bb  = board.white if player == 1 else board.black

    # 1) Positional: sum weights of my discs minus opp’s
    pos_score = 0
    for i, w in enumerate(SQUARE_WEIGHTS):
        mask = 1 << (63 - i)
        if my_bb & mask:
            pos_score += w
        elif opp_bb & mask:
            pos_score -= w

    # 2) Mobility: difference in legal move counts
    from jit_utils import legal_moves_jit
    import numpy as np
    my_moves_bb  = legal_moves_jit(np.uint64(my_bb),  np.uint64(opp_bb))
    opp_moves_bb = legal_moves_jit(np.uint64(opp_bb), np.uint64(my_bb))
    mob_score = (int(bin(int(my_moves_bb)).count('1'))
               - int(bin(int(opp_moves_bb)).count('1'))) * 5

    # 3) Corner occupancy bonus
    corners = [0, 7, 56, 63]
    corner_score = 0
    for c in corners:
        mask = 1 << c
        if my_bb & mask:
            corner_score += 25
        elif opp_bb & mask:
            corner_score -= 25

    return pos_score + mob_score + corner_score

if __name__ == "__main__":
    from board import Board
    from eval_utils import evaluate

    b = Board.start_pos()
    # At start, both sides have equal material & mobility ⇒ score ≈ 0
    s0 = evaluate(b, 1)
    print("Start-pos eval (Black):", s0)

    # Apply a typical opening move and re-eval
    moves = b.legal_moves(1)
    b.apply_move(moves[0], 1)
    s1 = evaluate(b, 1)
    print("After Black plays", moves[0], "eval:", s1)
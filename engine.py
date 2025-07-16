import numpy as np
from board import Board
from moves_utils import get_moves
from eval_utils import evaluate

def main():
    b = Board.start_pos()
    print("Starting position:\n")
    print(b, "\n")

    moves = get_moves(b, 1)
    print("Legal moves for Black:", moves, "\n")
    print("Eval (Black POV):", evaluate(b,1), "\n")

    mv = moves[0]
    b.apply_move(mv,1)
    print(f"After Black plays {mv}:\n")
    print(b, "\n")
    print("Eval (Black POV):", evaluate(b,1), "\n")

    b.undo()
    print("After undo:\n")
    print(b)

if __name__ == '__main__':
    main()
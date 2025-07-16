# moves_utils.py

from board import Board

def get_moves(board: Board, player: int) -> list[int]:
    """
    Return list of legal move indices (0–63) for `player`
    by calling the proven Python implementation.
    """
    return board.legal_moves(player)
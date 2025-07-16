# moves_utils.py

from board import Board


def get_moves(board: Board, player: int) -> list[int]:
    """Return list of legal move indices (0–63) for `player` using the built-in Board.legal_moves."""
    return board.legal_moves(player)

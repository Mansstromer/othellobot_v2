# board.py

class Board:
    """
    Bitboard-based Othello position using two 64-bit ints.
    Provides flat-FEN import/export, legal move generation,
    bitboard-based move application/undo, and pretty-print.
    """
    def __init__(self, black: int = 0, white: int = 0):
        self.black = black
        self.white = white
        self._history: list[tuple[int, int]] = []

    @classmethod
    def start_pos(cls):
        """Return the standard starting position."""
        # Bits: D4(27), E4(28), D5(35), E5(36)
        black = (1 << 28) | (1 << 35)
        white = (1 << 27) | (1 << 36)
        return cls(black, white)

    @classmethod
    def from_flat_fen(cls, fen: str):
        """Parse 64-char flat-FEN string (row-major, top row first)."""
        if len(fen) != 64:
            raise ValueError("flat-FEN must be 64 characters long")
        black = 0
        white = 0
        for idx, ch in enumerate(fen):
            mask = 1 << (63 - idx)
            if ch == 'X':
                black |= mask
            elif ch == 'O':
                white |= mask
        return cls(black, white)

    def to_flat_fen(self) -> str:
        """Serialize the board to a 64-character flat-FEN string."""
        out = []
        for i in range(64):
            mask = 1 << (63 - i)
            if self.black & mask:
                out.append('X')
            elif self.white & mask:
                out.append('O')
            else:
                out.append('.')
        return ''.join(out)

    @staticmethod
    def _directional_fill(gen: int, prop: int, shift: int, mask: int) -> int:
        """Kogge-Stone bitboard flip propagation helper."""
        flip = prop & mask & (gen << shift if shift > 0 else gen >> -shift)
        flip |= prop & mask & (flip << shift if shift > 0 else flip >> -shift)
        flip |= prop & mask & (flip << shift if shift > 0 else flip >> -shift)
        return flip

    def legal_moves(self, player: int) -> list[int]:
        """Return list of legal move indices (0–63); empty list means pass, via direct 2D scan."""
        # Build 2D array for current position
        board_arr = [['.' for _ in range(8)] for _ in range(8)]
        for idx in range(64):
            r, c = divmod(idx, 8)
            mask = 1 << (63 - idx)
            if self.black & mask:
                board_arr[r][c] = 'B'
            elif self.white & mask:
                board_arr[r][c] = 'W'

        you = 'B' if player == 1 else 'W'
        opp = 'W' if player == 1 else 'B'
        directions = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
        moves: list[int] = []

        for r in range(8):
            for c in range(8):
                if board_arr[r][c] != '.':
                    continue
                legal = False
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    found_opp = False
                    while 0 <= nr < 8 and 0 <= nc < 8 and board_arr[nr][nc] == opp:
                        found_opp = True
                        nr += dr; nc += dc
                    if found_opp and 0 <= nr < 8 and 0 <= nc < 8 and board_arr[nr][nc] == you:
                        legal = True
                        break
                if legal:
                    moves.append(r * 8 + c)
        return moves

    def apply_move(self, move: int, player: int) -> None:
        """
        Apply a move at index 0–63 for `player` (1=black, -1=white). 
        Flips captured discs by 2D directional scanning and pushes state for undo.
        """
        # Save state for undo
        self._history.append((self.black, self.white))

        # Build a 2D array representation
        board_arr = [['.' for _ in range(8)] for _ in range(8)]
        for idx in range(64):
            r, c = divmod(idx, 8)
            mask = 1 << (63 - idx)
            if self.black & mask:
                board_arr[r][c] = 'B'
            elif self.white & mask:
                board_arr[r][c] = 'W'

        # Place the new disc
        mr, mc = divmod(move, 8)
        you = 'B' if player == 1 else 'W'
        opp = 'W' if player == 1 else 'B'
        board_arr[mr][mc] = you

        # Directions: N, NE, E, SE, S, SW, W, NW
        directions = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
        to_flip = []
        for dr, dc in directions:
            line = []
            r, c = mr + dr, mc + dc
            # walk in this direction
            while 0 <= r < 8 and 0 <= c < 8 and board_arr[r][c] == opp:
                line.append((r,c))
                r += dr; c += dc
            # if bounded by a friendly disc, flip
            if 0 <= r < 8 and 0 <= c < 8 and board_arr[r][c] == you:
                to_flip.extend(line)

        # Apply flips
        for r, c in to_flip:
            board_arr[r][c] = you

        # Rebuild bitboards
        new_black = 0
        new_white = 0
        for r in range(8):
            for c in range(8):
                idx = r*8 + c
                mask = 1 << (63 - idx)
                if board_arr[r][c] == 'B':
                    new_black |= mask
                elif board_arr[r][c] == 'W':
                    new_white |= mask
        self.black, self.white = new_black, new_white

    def undo(self) -> None:
        """Undo the last move; restores previous bitboards."""
        if not self._history:
            raise IndexError("No moves to undo")
        self.black, self.white = self._history.pop()

# Quick self-test
if __name__ == '__main__':
    b = Board.start_pos()
    m = b.legal_moves(1)[0]
    b.apply_move(m, 1)
    b.undo()
    print("board.py OK")

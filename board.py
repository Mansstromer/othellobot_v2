import copy

class Board:
    """
    Bitboard-based Othello position using two 64-bit ints.
    Provides flat-FEN I/O, legal move generation helpers,
    apply/undo with history, and pretty-print.
    """
    def __init__(self, black: int = 0, white: int = 0):
        self.black = black
        self.white = white
        self._history: list[tuple[int, int]] = []

    # ─────────────────── initialization ───────────────────
    @classmethod
    def start_pos(cls):
        black = (1 << 28) | (1 << 35)   # E4 & D5
        white = (1 << 27) | (1 << 36)   # D4 & E5
        return cls(black, white)

    # ────────────────────── FEN I/O ───────────────────────
    @classmethod
    def from_flat_fen(cls, fen: str):
        if len(fen) != 64:
            raise ValueError("flat-FEN must be 64 chars")
        b = w = 0
        for idx, ch in enumerate(fen):
            m = 1 << (63 - idx)
            if ch == 'X':   b |= m
            elif ch == 'O': w |= m
        return cls(b, w)

    def to_flat_fen(self) -> str:
        out = []
        for i in range(64):
            m = 1 << (63 - i)
            out.append('X' if self.black & m else
                       'O' if self.white & m else '.')
        return ''.join(out)

    # ───────────────────── move helpers ───────────────────
    @staticmethod
    def _directional_fill(gen: int, prop: int, shift: int, mask: int) -> int:
        flip = prop & mask & (gen << shift if shift > 0 else gen >> -shift)
        flip |= prop & mask & (flip << shift if shift > 0 else flip >> -shift)
        flip |= prop & mask & (flip << shift if shift > 0 else flip >> -shift)
        return flip

    def legal_moves(self, player: int) -> list[int]:
        us   = self.black if player == 1 else self.white
        them = self.white if player == 1 else self.black
        empty = ~(us | them) & ((1 << 64) - 1)
        moves_bb = 0
        dirs  = [ 8, -8, 1, -1, 9, 7, -7, -9]
        masks = [0xFFFFFFFFFFFFFF00, 0x00FFFFFFFFFFFFFF,
                 0x7F7F7F7F7F7F7F7F, 0xFEFEFEFEFEFEFEFE,
                 0x007F7F7F7F7F7F00, 0x00FEFEFEFEFEFE00,
                 0x7F7F7F7F7F7F7F00, 0xFEFEFEFEFEFEFE00]
        for sh, ms in zip(dirs, masks):
            prop = self._directional_fill(us, them, sh, ms)
            moves_bb |= (prop << sh) if sh > 0 else (prop >> -sh)
        moves_bb &= empty

        moves, bb = [], moves_bb
        while bb:
            lsb = bb & -bb
            moves.append(lsb.bit_length() - 1)
            bb ^= lsb
        return moves

    # ──────────────────── apply / undo ────────────────────
    def apply_move(self, move: int, player: int):
        self._history.append((self.black, self.white))
        us   = self.black if player == 1 else self.white
        them = self.white if player == 1 else self.black
        flip = 0
        dirs  = [ 8, -8, 1, -1, 9, 7, -7, -9]
        masks = [0xFFFFFFFFFFFFFF00, 0x00FFFFFFFFFFFFFF,
                 0x7F7F7F7F7F7F7F7F, 0xFEFEFEFEFEFEFEFE,
                 0x007F7F7F7F7F7F00, 0x00FEFEFEFEFEFE00,
                 0x7F7F7F7F7F7F7F00, 0xFEFEFEFEFEFEFE00]
        for sh, ms in zip(dirs, masks):
            edge = (us << sh) & ((1 << 64)-1) if sh > 0 else (us >> -sh)
            flip |= self._directional_fill(edge, them, sh, ms)
        move_mask = 1 << move
        if player == 1:
            self.black = us | flip | move_mask
            self.white = them & ~flip
        else:
            self.white = us | flip | move_mask
            self.black = them & ~flip

    def undo(self):
        if not self._history:
            raise IndexError("undo stack empty")
        self.black, self.white = self._history.pop()

    # ─────────────────────── display ──────────────────────
    def __str__(self):
        rows = [self.to_flat_fen()[i*8:(i+1)*8] for i in range(8)]
        return '\n'.join(rows)

# quick self-test
if __name__ == '__main__':
    b = Board.start_pos()
    assert len(b.legal_moves(1)) == 4
    m = b.legal_moves(1)[0]
    b.apply_move(m,1); b.undo()
    print("board.py OK")
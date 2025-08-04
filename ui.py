import tkinter as tk
from board import Board
from moves_utils import get_moves
from engine import choose_move, TimeManager, load_opening_book

CELL_SIZE = 60
BOARD_COLOR = '#008000'
HIGHLIGHT_COLOR = '#ffff00'


class OthelloUI:
    """Simple Tkinter-based interface to play against the bot."""

    def __init__(self, root: tk.Tk, human_side: int) -> None:
        self.root = root
        self.human_side = human_side
        self.player = 1  # 1 = black, -1 = white
        self.ply = 0
        self.board = Board.start_pos()
        self.timer = TimeManager()
        self.book = load_opening_book()

        self.canvas = tk.Canvas(root, width=8 * CELL_SIZE, height=8 * CELL_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.draw_board()
        if self.player != self.human_side:
            # Bot starts the game
            self.root.after(100, self.bot_move)

    def draw_board(self) -> None:
        """Draw the grid and discs."""
        self.canvas.delete("all")
        # Squares
        for r in range(8):
            for c in range(8):
                x0 = c * CELL_SIZE
                y0 = r * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                self.canvas.create_rectangle(x0, y0, x1, y1,
                                              fill=BOARD_COLOR, outline='black')
        # Discs
        fen = self.board.to_flat_fen()
        for idx, ch in enumerate(fen):
            r, c = divmod(idx, 8)
            x0 = c * CELL_SIZE + 5
            y0 = r * CELL_SIZE + 5
            x1 = x0 + CELL_SIZE - 10
            y1 = y0 + CELL_SIZE - 10
            if ch == 'X':
                self.canvas.create_oval(x0, y0, x1, y1, fill='black')
            elif ch == 'O':
                self.canvas.create_oval(x0, y0, x1, y1, fill='white')

        # Highlight legal moves for human
        if self.player == self.human_side:
            moves = get_moves(self.board, self.player)
            for mv in moves:
                r, c = divmod(mv, 8)
                x0 = c * CELL_SIZE + 20
                y0 = r * CELL_SIZE + 20
                x1 = x0 + CELL_SIZE - 40
                y1 = y0 + CELL_SIZE - 40
                self.canvas.create_oval(x0, y0, x1, y1,
                                        outline=HIGHLIGHT_COLOR, width=2)

    def handle_click(self, event: tk.Event) -> None:
        """Handle user click on the board."""
        if self.player != self.human_side:
            return  # Not user's turn
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        idx = r * 8 + c
        moves = get_moves(self.board, self.player)
        if idx in moves:
            self.board.apply_move(idx, self.player)
            self.ply += 1
            self.player *= -1
            self.draw_board()
            self.root.after(100, self.bot_move)

    def bot_move(self) -> None:
        """Let the bot play if it's the bot's turn."""
        if self.player == self.human_side:
            return
        moves = get_moves(self.board, self.player)
        if moves:
            mv = choose_move(self.board, self.player, self.ply, self.timer, self.book)
            self.board.apply_move(mv, self.player)
            self.ply += 1
        self.player *= -1
        self.draw_board()
        if not (get_moves(self.board, 1) or get_moves(self.board, -1)):
            self.root.title("Game over")
        elif self.player != self.human_side:
            self.root.after(100, self.bot_move)


def main() -> None:
    side = input("Play as (b)lack or (w)hite? > ").strip().lower()
    human_side = 1 if side != 'w' else -1
    root = tk.Tk()
    root.title("Othello")
    OthelloUI(root, human_side)
    root.mainloop()


if __name__ == '__main__':
    main()


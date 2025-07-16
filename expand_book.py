# expand_book_symmetries.py

import json
from board import Board

# load your pruned book
with open("book.json") as f:
    base_book = json.load(f)

# 8 coordinate‐transform functions
def idx_identity(i: int) -> int:
    return i

def idx_rot90(i: int) -> int:
    r, c = divmod(i, 8)
    return (c * 8) + (7 - r)

def idx_rot180(i: int) -> int:
    return idx_rot90(idx_rot90(i))

def idx_rot270(i: int) -> int:
    return idx_rot90(idx_rot180(i))

def idx_reflect(i: int) -> int:
    r, c = divmod(i, 8)
    return r * 8 + (7 - c)

def idx_reflect_rot90(i: int) -> int:
    return idx_rot90(idx_reflect(i))

def idx_reflect_rot180(i: int) -> int:
    return idx_rot180(idx_reflect(i))

def idx_reflect_rot270(i: int) -> int:
    return idx_rot270(idx_reflect(i))

# matching fen‐transform functions
def rotate90(fen: str) -> str:
    return ''.join(fen[(7 - c)*8 + r] for r in range(8) for c in range(8))

def reflect(fen: str) -> str:
    return ''.join(fen[r*8 + (7 - c)] for r in range(8) for c in range(8))

def rot180(fen: str) -> str:
    return rotate90(rotate90(fen))

def rot270(fen: str) -> str:
    return rotate90(rotate90(rotate90(fen)))

def reflect_rot90(fen: str) -> str:
    return rotate90(reflect(fen))

def reflect_rot180(fen: str) -> str:
    return rot180(reflect(fen))

def reflect_rot270(fen: str) -> str:
    return rot270(reflect(fen))

# bundle them
transforms = [
    ("identity",        lambda f: f,                   idx_identity),
    ("rot90",           rotate90,                      idx_rot90),
    ("rot180",          rot180,                        idx_rot180),
    ("rot270",          rot270,                        idx_rot270),
    ("reflect",         reflect,                       idx_reflect),
    ("reflect_rot90",   reflect_rot90,                 idx_reflect_rot90),
    ("reflect_rot180",  reflect_rot180,                idx_reflect_rot180),
    ("reflect_rot270",  reflect_rot270,                idx_reflect_rot270),
]

expanded = {}

for fen, move in base_book.items():
    # determine side to play by stone counts
    bcount = fen.count("X")
    wcount = fen.count("O")
    player = 1 if bcount == wcount else -1

    # apply the stored move on a Board to handle any flip logic
    orig_board = Board.from_flat_fen(fen)
    orig_board.apply_move(move, player)
    new_fen = orig_board.to_flat_fen()

    for name, fen_fn, idx_fn in transforms:
        sym_fen   = fen_fn(fen)
        sym_new   = fen_fn(new_fen)
        # find the single bit difference in sym_new vs sym_fen
        for i in range(64):
            if sym_new[i] != sym_fen[i]:
                sym_move = i
                break
        else:
            # should never happen
            raise RuntimeError(f"No disc added for transform {name} on fen {fen}")

        expanded[sym_fen] = sym_move

# write out the full expanded book
with open("book_expanded.json", "w") as f:
    json.dump(expanded, f, indent=2)

print(f"Expanded {len(base_book)} → {len(expanded)} entries in book_expanded.json")
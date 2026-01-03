### IMPORTS
import chess


### BOARD SETUP
def print_board_unicode(board: chess.Board):
    files = "  a b c d e f g h"
    print(files)
    for rank in range(7, -1, -1):
        row = f"{rank + 1} "
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            row += (piece.unicode_symbol() if piece else "·") + " "
        print(row + str(rank + 1))
    print(files)

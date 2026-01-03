### IMPORTS
import chess
import sys
from chess_engine import ChessEngine
from display import print_board_unicode


### HUMAN PLAYER
class HumanEngine(ChessEngine):
    """human player (prompts for moves)"""
    
    def __init__(self):
        super().__init__("human")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        while True:
            print()
            print_board_unicode(board)
            print(f"\nlegal moves: {', '.join(board.san(m) for m in list(board.legal_moves)[:10])}", end="")
            if len(list(board.legal_moves)) > 10:
                print(f"... and {len(list(board.legal_moves)) - 10} more")
            else:
                print()
            
            move_str = input("\nenter your move (e.g., e2e4, Nf3, O-O): ").strip()
            
            if move_str.lower() in ['quit', 'exit', 'resign']:
                print("you resigned!")
                sys.exit(0)
            
            try:
                # try parsing as SAN (algebraic notation)
                move = board.parse_san(move_str)
                if move in board.legal_moves:
                    return move
                else:
                    print("illegal move!")
            except:
                try:
                    # try parsing as UCI (e2e4 format)
                    move = chess.Move.from_uci(move_str)
                    if move in board.legal_moves:
                        return move
                    else:
                        print("illegal move!")
                except:
                    print("invalid move format! use SAN (e.g., Nf3, e4) or UCI (e.g., e2e4)")

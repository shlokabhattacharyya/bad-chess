### IMPORTS
import chess
from chess_engine import ChessEngine
from human_engine import HumanEngine 


### GAME FUNCTION
def play_game(white_engine: ChessEngine, black_engine: ChessEngine, verbose: bool = True, max_moves: int = 200) -> str:
    """
    play a game between two engines
    returns: 'white', 'black', or 'draw'
    """
    board = chess.Board()
    white_engine.reset_state()
    black_engine.reset_state()
    
    move_count = 0
    
    while not board.is_game_over() and move_count < max_moves:
        current_engine = white_engine if board.turn == chess.WHITE else black_engine
        
        if verbose and isinstance(current_engine, HumanEngine):
            print(f"\n{'white' if board.turn == chess.WHITE else 'black'} to move")
        
        move = current_engine.get_move(board)
        
        if verbose:
            if isinstance(current_engine, HumanEngine):
                print(f"\nyou played: {board.san(move)}")
            else:
                print(f"{current_engine.name} plays: {board.san(move)}")
        
        board.push(move)
        move_count += 1
    
    if verbose:
        print("\n" + "="*50)
        print("GAME OVER")
        print("="*50)
        print("\nfinal position:")
        print(board)
        print()
    
    if board.is_checkmate():
        winner = 'white' if board.turn == chess.BLACK else 'black'
        if verbose:
            print(f"checkmate! {winner.capitalize()} wins!")
        return winner
    elif board.is_stalemate():
        if verbose:
            print("stalemate! draw.")
        return 'draw'
    elif board.is_insufficient_material():
        if verbose:
            print("insufficient material! draw.")
        return 'draw'
    elif board.can_claim_draw():
        if verbose:
            print("draw by repetition or 50-move rule.")
        return 'draw'
    elif move_count >= max_moves:
        if verbose:
            print(f"maximum moves ({max_moves}) reached. draw.")
        return 'draw'
    else:
        if verbose:
            print("game over (other reason). draw.")
        return 'draw'

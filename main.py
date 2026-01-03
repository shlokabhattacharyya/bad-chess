### IMPORTS
import argparse
from engine_registry import get_all_engines
from human_engine import HumanEngine
from game import play_game


### LIST ENGINES
def list_engines():
    """print all available engines with descriptions"""
    engines = get_all_engines()
    print("AVAILABLE CHESS ENGINES:\n")
    
    print("simple players:")
    simple_engines = {
        'random_move': 'random moves',
        'same_color': 'keeps pieces on same color squares',
        'opposite_color': 'keeps pieces on opposite color squares',
        'pacifist': 'avoids captures, checks, and checkmates',
        'first_move': 'lexicographically first legal move',
        'alphabetical': 'alphabetically first move (PGN)',
        'huddle': 'clusters pieces around own king',
        'swarm': 'attacks opponent king aggressively',
        'generous': 'offers pieces for capture',
        'no_i_insist': 'overwhelmingly polite gift-giving',
        'reverse_starting': 'tries to reach reversed starting position',
        'cccp': 'checkmate > check > capture > push',
        'suicide_king': 'brings kings together',
        'sym_mirror_y': 'vertical symmetry (copies opponent)',
        'sym_mirror_x': 'horizontal symmetry',
        'sym_180': '180° rotational symmetry',
        'min_oppt_moves': 'minimizes opponent options',
        'equalizer': 'moves pieces/squares equally',
    }
    
    for name, desc in simple_engines.items():
        print(f"  {name:20s} - {desc}")
    
    print()


### MAIN FUNCTION
def main():
    """main entry point for interactive play"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Elo World Chess Engines')
    parser.add_argument('--list', action='store_true', help='list all available engines')
    parser.add_argument('--engine', type=str, help='engine to play against')
    parser.add_argument('--color', type=str, choices=['white', 'black'], default='white',
                       help='your color (default: white)')
    
    args = parser.parse_args()
    
    if args.list:
        list_engines()
        return
    
    engines = get_all_engines()
    
    if args.engine:
        if args.engine not in engines:
            print(f"error: unknown engine '{args.engine}'")
            print("use --list to see available engines")
            return
        
        opponent = engines[args.engine]
    else:
        # interactive selection
        list_engines()
        while True:
            engine_name = input("choose an engine to play against: ").strip()
            if engine_name in engines:
                opponent = engines[engine_name]
                break
            print(f"unknown engine. please choose from the list above.")
    
    print(f"\nplaying against {opponent.name}")
    print(f"\nyou are playing as {args.color}")
    print("\nenter moves in algebraic notation (e.g., e4, Nf3) or UCI (e.g., e2e4)")
    print("\ntype 'quit' to resign\n")
    
    human = HumanEngine()
    
    if args.color == 'white':
        result = play_game(human, opponent, verbose=True)
    else:
        result = play_game(opponent, human, verbose=True)
    
    print(f"\nresult: {result}")


if __name__ == '__main__':
    main()

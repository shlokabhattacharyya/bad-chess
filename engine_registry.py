### IMPORTS
from typing import Dict
from chess_engine import ChessEngine

from engines.simple_players import (
    RandomMoveEngine,
    SameColorEngine,
    OppositeColorEngine,
    PacifistEngine,
    FirstMoveEngine,
    AlphabeticalEngine,
    HuddleEngine,
    SwarmEngine,
    GenerousEngine,
    NoIInsistEngine,
    ReverseStartingEngine,
    CCCPEngine,
    SuicideKingEngine,
    SymMirrorYEngine,
    SymMirrorXEngine,
    Sym180Engine,
    MinOpponentMovesEngine,
    EqualizerEngine,
)


### ENGINE REGISTRY
def get_all_engines() -> Dict[str, ChessEngine]:
    """returns dictionary of all available engines"""
    return {
        # simple players
        'random_move': RandomMoveEngine(),
        'same_color': SameColorEngine(),
        'opposite_color': OppositeColorEngine(),
        'pacifist': PacifistEngine(),
        'first_move': FirstMoveEngine(),
        'alphabetical': AlphabeticalEngine(),
        'huddle': HuddleEngine(),
        'swarm': SwarmEngine(),
        'generous': GenerousEngine(),
        'no_i_insist': NoIInsistEngine(),
        'reverse_starting': ReverseStartingEngine(),
        'cccp': CCCPEngine(),
        'suicide_king': SuicideKingEngine(),
        'sym_mirror_y': SymMirrorYEngine(),
        'sym_mirror_x': SymMirrorXEngine(),
        'sym_180': Sym180Engine(),
        'min_oppt_moves': MinOpponentMovesEngine(),
        'equalizer': EqualizerEngine(),
        
    }

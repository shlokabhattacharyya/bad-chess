### IMPORTS
import chess
from abc import ABC, abstractmethod


### BASE CLASS
class ChessEngine(ABC):
    """base class for all chess engines"""

    def __init__(self, name: str):
        self.name = name
        self.state = {}  # for stateful engines
    
    @abstractmethod
    def get_move(self, board: chess.Board) -> chess.Move:
        """return a move for the given board position"""
        pass
    
    def reset_state(self):
        """reset any internal state between games"""
        self.state = {}

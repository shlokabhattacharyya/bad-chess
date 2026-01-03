### IMPORTS
import chess
import random
from chess_engine import ChessEngine


### SIMPLE PLAYERS
class RandomMoveEngine(ChessEngine):
    """choose a legal move uniformly at random"""
    
    def __init__(self):
        super().__init__("random_move")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        return random.choice(list(board.legal_moves))


class SameColorEngine(ChessEngine):
    """when playing as white, put pieces on white squares. vice versa for black."""
    
    def __init__(self):
        super().__init__("same_color")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        best_moves = []
        best_score = -1
        
        our_color = board.turn
        
        for move in board.legal_moves:
            board.push(move)
            score = self._count_same_color(board, our_color)
            board.pop()
            
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves) if best_moves else random.choice(list(board.legal_moves))
    
    def _count_same_color(self, board: chess.Board, color: chess.Color) -> int:
        count = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color:
                square_is_light = (chess.square_file(square) + chess.square_rank(square)) % 2 == 1
                piece_is_white = color == chess.WHITE
                if square_is_light == piece_is_white:
                    count += 1
        return count


class OppositeColorEngine(ChessEngine):
    """same idea as above, opposite parity"""
    
    def __init__(self):
        super().__init__("opposite_color")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        best_moves = []
        best_score = -1
        
        our_color = board.turn
        
        for move in board.legal_moves:
            board.push(move)
            score = self._count_opposite_color(board, our_color)
            board.pop()
            
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves) if best_moves else random.choice(list(board.legal_moves))
    
    def _count_opposite_color(self, board: chess.Board, color: chess.Color) -> int:
        count = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color:
                square_is_light = (chess.square_file(square) + chess.square_rank(square)) % 2 == 1
                piece_is_white = color == chess.WHITE
                if square_is_light != piece_is_white:
                    count += 1
        return count


class PacifistEngine(ChessEngine):
    """avoid moves that mate, check, capture. capture lower value pieces if forced."""
    
    def __init__(self):
        super().__init__("pacifist")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        legal_moves = list(board.legal_moves)
        
        # tier 1: avoid checkmate
        non_mate_moves = []
        for move in legal_moves:
            board.push(move)
            is_mate = board.is_checkmate()
            board.pop()
            if not is_mate:
                non_mate_moves.append(move)
        
        if non_mate_moves:
            legal_moves = non_mate_moves
        
        # tier 2: avoid checks
        non_check_moves = []
        for move in legal_moves:
            board.push(move)
            is_check = board.is_check()
            board.pop()
            if not is_check:
                non_check_moves.append(move)
        
        if non_check_moves:
            legal_moves = non_check_moves
        
        # tier 3: avoid captures, prefer lower value captures
        non_capture_moves = [m for m in legal_moves if not board.is_capture(m)]
        
        if non_capture_moves:
            return random.choice(non_capture_moves)
        
        # if we must capture, prefer lower value pieces
        piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, 
                       chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
        
        def capture_value(move):
            captured = board.piece_at(move.to_square)
            return piece_values.get(captured.piece_type, 0) if captured else 0
        
        legal_moves.sort(key=capture_value)
        min_value = capture_value(legal_moves[0])
        min_captures = [m for m in legal_moves if capture_value(m) == min_value]
        
        return random.choice(min_captures)


class FirstMoveEngine(ChessEngine):
    """make the lexicographically first legal move"""
    
    def __init__(self):
        super().__init__("first_move")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        
        # sort by source square, then destination, then promotion
        def move_key(move):
            from_sq = move.from_square
            to_sq = move.to_square
            promo = move.promotion if move.promotion else 0
            
            # reverse rows for black to maintain symmetry
            if not board.turn:  # black
                from_rank = 7 - chess.square_rank(from_sq)
                to_rank = 7 - chess.square_rank(to_sq)
                from_sq = chess.square(chess.square_file(from_sq), from_rank)
                to_sq = chess.square(chess.square_file(to_sq), to_rank)
            
            return (from_sq, to_sq, promo)
        
        moves.sort(key=move_key)
        return moves[0]


class AlphabeticalEngine(ChessEngine):
    """make the alphabetically first move using standard PGN short notation"""
    
    def __init__(self):
        super().__init__("alphabetical")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        moves = list(board.legal_moves)
        moves.sort(key=lambda m: board.san(m))
        return moves[0]


class HuddleEngine(ChessEngine):
    """minimize total distance between own pieces and own king"""
    
    def __init__(self):
        super().__init__("huddle")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        best_moves = []
        best_score = float('inf')
        
        our_color = board.turn
        
        for move in board.legal_moves:
            board.push(move)
            score = self._total_distance_to_king(board, our_color)
            board.pop()
            
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves)
    
    def _total_distance_to_king(self, board: chess.Board, color: chess.Color) -> int:
        king_square = board.king(color)
        if king_square is None:
            return 0
        
        total = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color and piece.piece_type != chess.KING:
                total += self._chebyshev_distance(square, king_square)
        return total
    
    def _chebyshev_distance(self, sq1: int, sq2: int) -> int:
        """king's distance (max of file and rank differences)"""
        file_diff = abs(chess.square_file(sq1) - chess.square_file(sq2))
        rank_diff = abs(chess.square_rank(sq1) - chess.square_rank(sq2))
        return max(file_diff, rank_diff)


class SwarmEngine(ChessEngine):
    """move pieces to minimize distance to opponent's king (creates all-out attack)"""
    
    def __init__(self):
        super().__init__("swarm")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        best_moves = []
        best_score = float('inf')
        
        our_color = board.turn
        opponent_color = not board.turn
        
        for move in board.legal_moves:
            board.push(move)
            score = self._total_distance_to_king(board, our_color, opponent_color)
            board.pop()
            
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves)
    
    def _total_distance_to_king(self, board: chess.Board, 
                                our_color: chess.Color, 
                                opponent_color: chess.Color) -> int:
        king_square = board.king(opponent_color)
        if king_square is None:
            return 0
        
        total = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == our_color:
                file_diff = abs(chess.square_file(square) - chess.square_file(king_square))
                rank_diff = abs(chess.square_rank(square) - chess.square_rank(king_square))
                total += max(file_diff, rank_diff)
        return total


class GenerousEngine(ChessEngine):
    """maximize pieces offered for capture, weighted by piece value"""
    
    def __init__(self):
        super().__init__("generous")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
                       chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
        
        best_moves = []
        best_score = -1
        
        our_color = board.turn
        
        for move in board.legal_moves:
            board.push(move)
            
            # count what opponent can capture (our pieces)
            score = 0
            for opp_move in board.legal_moves:
                if board.is_capture(opp_move):
                    captured = board.piece_at(opp_move.to_square)
                    # Make sure we're capturing OUR pieces
                    if captured and captured.color == our_color:
                        score += piece_values.get(captured.piece_type, 0)
            
            board.pop()
            
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves) if best_moves else random.choice(list(board.legal_moves))


class NoIInsistEngine(ChessEngine):
    """similar to generous but overwhelmingly polite, tries to force opponent to accept gifts"""
    
    def __init__(self):
        super().__init__("no_i_insist")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
                       chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
        
        legal_moves = list(board.legal_moves)
        our_color = board.turn
        
        # tier 1: avoid checkmate (it's rude), prefer stalemate
        non_mate_moves = []
        stalemate_moves = []
        for move in legal_moves:
            board.push(move)
            if board.is_checkmate():
                pass  # don't add
            elif board.is_stalemate():
                stalemate_moves.append(move)
            else:
                non_mate_moves.append(move)
            board.pop()
        
        if stalemate_moves:
            return random.choice(stalemate_moves)
        if non_mate_moves:
            legal_moves = non_mate_moves
        
        # tier 2: prefer moves where opponent MUST capture our piece
        forced_capture_moves = []
        for move in legal_moves:
            board.push(move)
            
            # check if ALL opponent moves are captures of our pieces
            opp_moves = list(board.legal_moves)
            if opp_moves:
                our_captures = [m for m in opp_moves if board.is_capture(m)]
                if our_captures:
                    # Check if they're all capturing OUR pieces
                    all_capture_us = all(
                        board.piece_at(m.to_square) and board.piece_at(m.to_square).color == our_color
                        for m in our_captures
                    )
                    if all_capture_us and len(our_captures) == len(opp_moves):
                        # find highest value piece that must be captured
                        max_forced_value = 0
                        for opp_move in our_captures:
                            captured = board.piece_at(opp_move.to_square)
                            if captured:
                                val = piece_values.get(captured.piece_type, 0)
                                max_forced_value = max(max_forced_value, val)
                        forced_capture_moves.append((move, max_forced_value))
            
            board.pop()
        
        if forced_capture_moves:
            # choose move that forces capture of highest value piece
            forced_capture_moves.sort(key=lambda x: x[1], reverse=True)
            best_val = forced_capture_moves[0][1]
            best = [m for m, v in forced_capture_moves if v == best_val]
            return random.choice(best)
        
        # tier 3: maximize expected value of offered material
        best_moves = []
        best_score = -1
        
        for move in legal_moves:
            board.push(move)
            
            # calculate expected value of captures of OUR pieces
            opp_moves = list(board.legal_moves)
            if opp_moves:
                total_value = 0
                capture_count = 0
                for opp_move in opp_moves:
                    if board.is_capture(opp_move):
                        captured = board.piece_at(opp_move.to_square)
                        if captured and captured.color == our_color:
                            total_value += piece_values.get(captured.piece_type, 0)
                            capture_count += 1
                
                score = total_value / len(opp_moves) if opp_moves else 0
            else:
                score = 0
            
            board.pop()
            
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves) if best_moves else random.choice(legal_moves)


class ReverseStartingEngine(ChessEngine):
    """tries to put pieces where the opponent's pieces start (board upside-down)"""
    
    def __init__(self):
        super().__init__("reverse_starting")
        
        # define target positions (reversed board)
        # white pieces try to reach black's starting positions
        self.white_targets = {
            chess.PAWN: [chess.A7, chess.B7, chess.C7, chess.D7, chess.E7, chess.F7, chess.G7, chess.H7],
            chess.ROOK: [chess.A8, chess.H8],
            chess.KNIGHT: [chess.B8, chess.G8],
            chess.BISHOP: [chess.C8, chess.F8],
            chess.QUEEN: [chess.D8],
            chess.KING: [chess.E8]
        }
        
        self.black_targets = {
            chess.PAWN: [chess.A2, chess.B2, chess.C2, chess.D2, chess.E2, chess.F2, chess.G2, chess.H2],
            chess.ROOK: [chess.A1, chess.H1],
            chess.KNIGHT: [chess.B1, chess.G1],
            chess.BISHOP: [chess.C1, chess.F1],
            chess.QUEEN: [chess.D1],
            chess.KING: [chess.E1]
        }
    
    def get_move(self, board: chess.Board) -> chess.Move:
        best_moves = []
        best_score = float('inf')
        
        our_color = board.turn
        
        for move in board.legal_moves:
            board.push(move)
            score = self._distance_from_targets(board, our_color)
            board.pop()
            
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves)
    
    def _distance_from_targets(self, board: chess.Board, color: chess.Color) -> float:
        targets = self.white_targets if color == chess.WHITE else self.black_targets
        total_distance = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color:
                piece_targets = targets.get(piece.piece_type, [])
                if piece_targets:
                    # Find minimum distance to any target square for this piece type
                    min_dist = min(self._piece_distance(square, target, piece.piece_type) 
                                  for target in piece_targets)
                    total_distance += min_dist
        
        return total_distance
    
    def _piece_distance(self, sq1: int, sq2: int, piece_type: int) -> float:
        """distance metric based on piece type"""
        if piece_type == chess.KING:
            # Chebyshev distance for king
            return max(abs(chess.square_file(sq1) - chess.square_file(sq2)),
                      abs(chess.square_rank(sq1) - chess.square_rank(sq2)))
        elif piece_type == chess.ROOK:
            # Manhattan distance for rook
            return abs(chess.square_file(sq1) - chess.square_file(sq2)) + \
                   abs(chess.square_rank(sq1) - chess.square_rank(sq2))
        elif piece_type == chess.KNIGHT:
            # approximate knight distance
            file_diff = abs(chess.square_file(sq1) - chess.square_file(sq2))
            rank_diff = abs(chess.square_rank(sq1) - chess.square_rank(sq2))
            return max(file_diff, rank_diff) + min(file_diff, rank_diff) / 2
        else:
            # default to Chebyshev
            return max(abs(chess.square_file(sq1) - chess.square_file(sq2)),
                      abs(chess.square_rank(sq1) - chess.square_rank(sq2)))


class CCCPEngine(ChessEngine):
    """checkmate, check, capture, push"""
    
    def __init__(self):
        super().__init__("cccp")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        legal_moves = list(board.legal_moves)
        
        # tier 1: checkmate
        for move in legal_moves:
            board.push(move)
            if board.is_checkmate():
                board.pop()
                return move
            board.pop()
        
        # tier 2: check
        check_moves = []
        for move in legal_moves:
            board.push(move)
            if board.is_check():
                check_moves.append(move)
            board.pop()
        
        if check_moves:
            legal_moves = check_moves
        
        # tier 3: capture
        capture_moves = [m for m in legal_moves if board.is_capture(m)]
        if capture_moves:
            legal_moves = capture_moves
        
        # tier 4: push (advance into enemy territory)
        def push_score(move):
            to_rank = chess.square_rank(move.to_square)
            return to_rank if board.turn == chess.WHITE else (7 - to_rank)
        
        legal_moves.sort(key=push_score, reverse=True)
        best_push = push_score(legal_moves[0])
        best_moves = [m for m in legal_moves if push_score(m) == best_push]
        
        # break ties deterministically
        best_moves.sort(key=lambda m: (m.from_square, m.to_square))
        return best_moves[0]


class SuicideKingEngine(ChessEngine):
    """minimize distance between the two kings (putting king in danger)"""
    
    def __init__(self):
        super().__init__("suicide_king")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        our_color = board.turn
        opp_color = not board.turn
        
        our_king = board.king(our_color)
        opp_king = board.king(opp_color)
        
        if our_king is None or opp_king is None:
            return random.choice(list(board.legal_moves))
        
        best_moves = []
        best_distance = float('inf')
        
        for move in board.legal_moves:
            board.push(move)
            
            # recalculate king positions after move
            new_our_king = board.king(our_color)
            new_opp_king = board.king(opp_color)
            
            if new_our_king and new_opp_king:
                file_diff = abs(chess.square_file(new_our_king) - chess.square_file(new_opp_king))
                rank_diff = abs(chess.square_rank(new_our_king) - chess.square_rank(new_opp_king))
                distance = max(file_diff, rank_diff)
                
                if distance < best_distance:
                    best_distance = distance
                    best_moves = [move]
                elif distance == best_distance:
                    best_moves.append(move)
            
            board.pop()
        
        return random.choice(best_moves) if best_moves else random.choice(list(board.legal_moves))


class SymMirrorYEngine(ChessEngine):
    """maximize vertical symmetry"""
    
    def __init__(self):
        super().__init__("sym_mirror_y")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        best_moves = []
        best_score = float('inf')
        
        for move in board.legal_moves:
            board.push(move)
            score = self._vertical_asymmetry(board)
            board.pop()
            
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves)
    
    def _vertical_asymmetry(self, board: chess.Board) -> int:
        penalty = 0
        for file in range(8):
            for rank in range(4):
                sq1 = chess.square(file, rank)
                sq2 = chess.square(file, 7 - rank)
                
                p1 = board.piece_at(sq1)
                p2 = board.piece_at(sq2)
                
                if p1 is None and p2 is None:
                    continue
                elif p1 is None or p2 is None:
                    penalty += 2
                elif p1.piece_type != p2.piece_type:
                    penalty += 1
                elif p1.color == p2.color:
                    penalty += 2
        
        return penalty


class SymMirrorXEngine(ChessEngine):
    """maximize horizontal symmetry"""
    
    def __init__(self):
        super().__init__("sym_mirror_x")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        best_moves = []
        best_score = float('inf')
        
        for move in board.legal_moves:
            board.push(move)
            score = self._horizontal_asymmetry(board)
            board.pop()
            
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves)
    
    def _horizontal_asymmetry(self, board: chess.Board) -> int:
        penalty = 0
        for rank in range(8):
            for file in range(4):
                sq1 = chess.square(file, rank)
                sq2 = chess.square(7 - file, rank)
                
                p1 = board.piece_at(sq1)
                p2 = board.piece_at(sq2)
                
                if p1 is None and p2 is None:
                    continue
                elif p1 is None or p2 is None:
                    penalty += 2
                elif p1.piece_type != p2.piece_type:
                    penalty += 1
                elif p1.color == p2.color:
                    penalty += 2
        
        return penalty


class Sym180Engine(ChessEngine):
    """maximize 180-degrees rotational symmetry"""
    
    def __init__(self):
        super().__init__("sym_180")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        best_moves = []
        best_score = float('inf')
        
        for move in board.legal_moves:
            board.push(move)
            score = self._rotation_asymmetry(board)
            board.pop()
            
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves)
    
    def _rotation_asymmetry(self, board: chess.Board) -> int:
        penalty = 0
        for square in chess.SQUARES:
            if square >= 32:  # only check half the board
                break
            
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            
            # 180-degrees rotation
            rot_file = 7 - file
            rot_rank = 7 - rank
            rot_square = chess.square(rot_file, rot_rank)
            
            p1 = board.piece_at(square)
            p2 = board.piece_at(rot_square)
            
            if p1 is None and p2 is None:
                continue
            elif p1 is None or p2 is None:
                penalty += 2
            elif p1.piece_type != p2.piece_type:
                penalty += 1
            elif p1.color == p2.color:
                penalty += 2
        
        return penalty


class MinOpponentMovesEngine(ChessEngine):
    """minimize the number of legal moves for opponent"""
    
    def __init__(self):
        super().__init__("min_oppt_moves")
    
    def get_move(self, board: chess.Board) -> chess.Move:
        best_moves = []
        best_score = float('inf')
        
        for move in board.legal_moves:
            board.push(move)
            score = len(list(board.legal_moves))
            board.pop()
            
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        return random.choice(best_moves)


class EqualizerEngine(ChessEngine):
    """move pieces that have been moved least to squares visited least"""
    
    def __init__(self):
        super().__init__("equalizer")
    
    def reset_state(self):
        self.state = {
            'piece_moves': {},  # piece_id -> move_count
            'square_visits': {sq: 0 for sq in chess.SQUARES},
            'piece_ids': {}  # square -> piece_id (to track pieces)
        }
        
        # initialize piece IDs based on starting position
        board = chess.Board()
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                self.state['piece_ids'][square] = (square, piece.piece_type, piece.color)
                self.state['piece_moves'][(square, piece.piece_type, piece.color)] = 0
    
    def get_move(self, board: chess.Board) -> chess.Move:
        if not self.state:
            self.reset_state()
        
        best_moves = []
        best_score = (float('inf'), float('inf'))
        
        for move in board.legal_moves:
            piece = board.piece_at(move.from_square)
            if not piece:
                continue
            
            # try to find piece ID
            piece_id = self.state['piece_ids'].get(move.from_square)
            if not piece_id:
                piece_id = (move.from_square, piece.piece_type, piece.color)
            
            piece_move_count = self.state['piece_moves'].get(piece_id, 0)
            square_visit_count = self.state['square_visits'].get(move.to_square, 0)
            
            score = (piece_move_count, square_visit_count)
            
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        chosen_move = random.choice(best_moves) if best_moves else random.choice(list(board.legal_moves))
        
        # update state
        piece = board.piece_at(chosen_move.from_square)
        if piece:
            piece_id = self.state['piece_ids'].get(chosen_move.from_square, 
                                                   (chosen_move.from_square, piece.piece_type, piece.color))
            self.state['piece_moves'][piece_id] = self.state['piece_moves'].get(piece_id, 0) + 1
            self.state['square_visits'][chosen_move.to_square] = self.state['square_visits'].get(chosen_move.to_square, 0) + 1
            
            # update piece tracking
            if chosen_move.from_square in self.state['piece_ids']:
                del self.state['piece_ids'][chosen_move.from_square]
            self.state['piece_ids'][chosen_move.to_square] = piece_id
            
            # handle castling
            if board.is_castling(chosen_move):
                if chosen_move.to_square > chosen_move.from_square:  # kingside
                    rook_from = chosen_move.to_square + 1
                    rook_to = chosen_move.to_square - 1
                else:  # queenside
                    rook_from = chosen_move.to_square - 2
                    rook_to = chosen_move.to_square + 1
                
                rook_id = self.state['piece_ids'].get(rook_from)
                if rook_id:
                    self.state['piece_moves'][rook_id] = self.state['piece_moves'].get(rook_id, 0) + 1
                    self.state['square_visits'][rook_to] = self.state['square_visits'].get(rook_to, 0) + 1
                    del self.state['piece_ids'][rook_from]
                    self.state['piece_ids'][rook_to] = rook_id
        
        return chosen_move

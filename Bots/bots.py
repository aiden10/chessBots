"""
Iterating over board:

def iterate_board(board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            print(piece.piece_type)
            print(piece.color)
            print(piece.symbol())
"""

import random
import chess
from PyQt5.QtWidgets import QInputDialog
class HumanNotBot:
    """
    "Bot" which allows humans to make moves.
    """
    def __init__(self):
        self.name = 'Me'
        self.side = None
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def get_move(self, board):
        legal_moves = list(board.legal_moves)
        moves_string = ''
        san_moves = [board.san(m) for m in legal_moves]
        for m in san_moves:
            moves_string += f'{m}\n'
        move, ok = QInputDialog.getText(None, "Enter Move", f"{moves_string}Enter your move:")
        if ok:
            move = board.parse_san(move)
            if move in legal_moves:
                return move
        return None

class RandomBot:
    """
    Bot which only makes random valid moves
    """
    def __init__(self):
        self.name = 'Random Bot'
        self.side = None
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def get_move(self, board):
        move = random.choice(list(board.legal_moves))
        return move

class BasicEvalBot:
    """
    Bot which evaluates the state of the board at each legal move and takes the best one.
    Evaluation is simple and only consists of summing the values of each piece. What this actually
    means is that all it does is capture a piece if it can, otherwise it moves randomly.
    """
    def __init__(self):
        self.name = 'B.E.B'
        self.side = None
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  
        }

    def evaluate(self, board):
        white_sum = 0
        black_sum = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                value = self.piece_values[piece.piece_type]
                if piece.color == chess.WHITE:
                    white_sum += value
                else:
                    black_sum += value
        
        return white_sum, black_sum

    def get_move(self, board):
        """
        Needs to consider the move which causes the opponent's worst state as its best move rather than looking at the move
        which causes its best state because your moves can only capture the enemy pieces. The downside to this is that it really means
        that all it does is simply capture the most valuable piece if possible, otherwise it makes a random move.
        """
        legal_moves = list(board.legal_moves)
        results = []
        for move in legal_moves:
            temp_board = board.copy()
            temp_board.push(move)
            white_sum, black_sum = self.evaluate(temp_board) # evaluate moves
            result = {
                "move": move,
                "white_sum": white_sum,
                "black_sum": black_sum
            }
            results.append(result)

        if self.side == chess.WHITE:
            best_result = min(results, key=lambda x: x["black_sum"])
            worst_result = max(results, key=lambda x: x["black_sum"])

        else:
            best_result = min(results, key=lambda x: x["white_sum"])
            worst_result = max(results, key=lambda x: x["white_sum"])
        
        best_move = best_result["move"]

        # if no move results in a capture, do a random move
        if best_result == worst_result:
            best_move = random.choice(legal_moves) 
        
        return best_move

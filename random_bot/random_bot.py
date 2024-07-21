import random

class RandomBot:
    def __init__(self):
        self.name = 'Random Bot'
        self.side = None
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def get_move(self, board):
        move = random.choice(list(board.legal_moves))
        return move

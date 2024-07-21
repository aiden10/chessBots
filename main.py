"""
Interface for pitting bots against one another
"""

import chess
import chess.svg
import random
import time

from random_bot.random_bot import RandomBot
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import QByteArray

def play_games(games, bot1, bot2):
    for _ in range(games):
        board = chess.Board()
        if random.choice([0, 1]) == 1:
            bot1_turn = True
            bot1.side = chess.WHITE
            bot2.side = chess.BLACK
        else:
            bot1_turn = False
            bot1.side = chess.BLACK
            bot2.side = chess.WHITE

        while not board.is_game_over():
            if bot1_turn:
                move = bot1.get_move(board)
            else:
                move = bot2.get_move(board)

            board.push(move)
            bot1_turn = not bot1_turn

        outcome = board.outcome()
        if outcome:
            winner = outcome.winner

            # game is a draw
            if outcome.termination in [chess.Termination.STALEMATE, chess.Termination.INSUFFICIENT_MATERIAL, chess.Termination.THREEFOLD_REPETITION, chess.Termination.FIFTY_MOVES]:
                bot1.draws += 1
                bot2.draws += 1

            # bot1 wins
            elif (winner == chess.WHITE and bot1.side == chess.WHITE) or (winner == chess.BLACK and bot1.side == chess.BLACK):
                bot1.wins += 1
                bot2.losses += 1

            # bot2 wins
            else:
                bot1.losses += 1
                bot2.wins += 1

    print('Games completed')

class MainWindow(QWidget):
    def __init__(self, bot1, bot2):
        super().__init__()
        # chess properties
        self.bot1 = bot1
        self.bot2 = bot2
        self.bot1_turn = None
        self.board = None

        self.setGeometry(0, 0, 800, 900)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.widgetSvg = QSvgWidget()
        self.widgetSvg.setGeometry(0, 50, 800, 800)
        layout.addWidget(self.widgetSvg)

        self.button = QPushButton("Make Move")
        self.button.clicked.connect(self.make_move)
        layout.addWidget(self.button)

        self.start_game()

    def start_game(self):
        if random.choice([0, 1]) == 1:
            self.bot1_turn = True
            self.bot1.side = chess.WHITE
            self.bot2.side = chess.BLACK
        else:
            self.bot1_turn = False
            self.bot1.side = chess.BLACK
            self.bot2.side = chess.WHITE

        self.board = chess.Board()
        self.display_board()

    def display_board(self):
        svg_data = chess.svg.board(board=self.board).encode('UTF-8')
        self.widgetSvg.load(QByteArray(svg_data))

    def make_move(self):
        if not self.board.is_game_over():
            if self.bot1_turn:
                move = self.bot1.get_move(self.board)
            else:
                move = self.bot2.get_move(self.board)

            self.board.push(move)
            self.bot1_turn = not self.bot1_turn
            self.display_board()

        else:
            outcome = self.board.outcome()
            if outcome:
                winner = outcome.winner

                # game is a draw
                if outcome.termination in [chess.Termination.STALEMATE, chess.Termination.INSUFFICIENT_MATERIAL, chess.Termination.THREEFOLD_REPETITION, chess.Termination.FIFTY_MOVES]:
                    print('Draw')
                    self.bot1.draws += 1
                    self.bot2.draws += 1

                # bot1 wins
                elif (winner == chess.WHITE and self.bot1.side == chess.WHITE) or (winner == chess.BLACK and self.bot1.side == chess.BLACK):
                    self.bot1.wins += 1
                    self.bot2.losses += 1
                    print(f'{self.bot1.name} Wins')

                # bot2 wins
                else:
                    self.bot1.losses += 1
                    self.bot2.wins += 1
                    print(f'{self.bot2.name} Wins')
                
                # Display restart button and text for which bot won 

app = QApplication([])
bot1, bot2 = RandomBot(), RandomBot()
window = MainWindow(bot1, bot2)

window.show()
app.exec_()


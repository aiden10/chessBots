"""
Interface for pitting bots against one another using https://python-chess.readthedocs.io/en/latest/
Each chess bot simply needs to have the following properties and a get_move function which takes in the board object.
Example:
    class chessBot:
        def __init__():
            self.name = 'Bot'
            self.side = None
            self.wins = 0
            self.losses = 0
            self.draws = 0

        def get_move(self, board): 
            # implement move calculation logic
            return move

"""

import chess
import chess.svg
import random
import json
import datetime
import os

from Bots.bots import RandomBot, HumanNotBot, BasicEvalBot

from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QSizePolicy, QMessageBox, QCheckBox
from PyQt5.QtCore import QByteArray, Qt, QTimer

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def play_games(games, bot1, bot2):
    for i in range(1, games+1):
        print(f'Game {i}/{games}')
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

    print('\nGames completed\n')
    print('Game Stats:')
    print(f'Draw %: {(bot1.draws/games) * 100}%')
    print(f'{bot1.name} winrate: {bot1.wins/games}%')
    print(f'{bot2.name} winrate: {bot2.wins/games}%')
    print(f'{bot1.name} # of wins: {bot1.wins}')
    print(f'{bot2.name} # of wins: {bot2.wins}')

def save_recording(move_list, bot1, bot2):
    now = datetime.datetime.now()

    title = f'({bot1.name})VS({bot2.name})-{now.day}-{now.hour}-{now.minute}-{now.second}.json'
    with open(f'{CURRENT_DIR}/recordings/{title}', 'w') as file:
        if bot1.side == chess.BLACK: 
            bot1_side = 'Black'
            bot2_side = 'White'
        else:
            bot1_side = 'White'
            bot2_side = 'Black'
        data = {
                "Bot1": {
                    "Name": bot1.name,
                    "Side": bot1_side
                    },
                "Bot2": {
                    "Name": bot2.name,
                    "Side": bot2_side
                    },
                    "Moves": move_list
                }
        json.dump(data, file, indent=4)
    
    msg = QMessageBox()
    msg.setWindowTitle('Record Game')
    msg.setText(f'Game Successfully Saved\nThe recording can be found at {CURRENT_DIR}/recordings/{title}')
    msg.exec_()

def prompt_recording(moves, bot1, bot2):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle('Record Game')
    msg.setText('Record previous game?')
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)
    
    def handle_button_click(response):
        if response == QMessageBox.Yes:
            save_recording(moves, bot1, bot2)
        msg.close()

    msg.buttonClicked.connect(lambda btn: handle_button_click(msg.standardButton(btn)))
    msg.exec_()

class MainWindow(QWidget):
    def __init__(self, bot1, bot2):
        super().__init__()
        # Chess properties
        self.bot1 = bot1
        self.bot2 = bot2
        self.bot1_turn = None
        self.board = None
        self.moves = []

        # Window settings
        self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT + 150)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.widgetSvg = QSvgWidget()
        self.widgetSvg.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        layout.addWidget(self.widgetSvg)

        # Labels
        self.bot1_label = QLabel()
        self.bot2_label = QLabel()
        self.bot1_label.setMaximumHeight(50)
        self.bot2_label.setMaximumHeight(50)
        self.bot1_label.setAlignment(Qt.AlignCenter)
        self.bot2_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.bot2_label)
        layout.addWidget(self.bot1_label)
        
        # Move Button
        self.moveButton = QPushButton("Make Move")
        self.moveButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.moveButton.setFixedSize(WINDOW_WIDTH, 100)
        self.moveButton.clicked.connect(self.make_move)
        layout.addWidget(self.moveButton)

        # Auto move checkbox
        self.auto_move_checkbox = QCheckBox("Auto Move")
        self.auto_move_checkbox.stateChanged.connect(self.toggle_auto_move)
        layout.addWidget(self.auto_move_checkbox)

        self.auto_move_timer = QTimer(self)
        self.auto_move_timer.timeout.connect(self.make_move)
        self.auto_move_timer.setInterval(200)  # 5 moves per second (1000ms / 5 = 200ms)
        self.start_game()

    def toggle_auto_move(self, state):
        if state == Qt.Checked:
            self.auto_move_timer.start()
            self.moveButton.setEnabled(False)
        else:
            self.auto_move_timer.stop()
            self.moveButton.setEnabled(True)

    def display_winner(self, winner, loser, moves, draw=False):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Game Over")
        self.moveButton.setDisabled(True)

        if not draw:
            text = f'{winner.name} Wins in {len(moves)} moves\nPlay again?'
        else:
            text = f'Draw after {len(moves)} moves\nPlay again?'
        
        dialog.setText(text)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.Yes)
        
        result = dialog.exec_()
        
        if result == QMessageBox.Yes:
            self.start_game()
        else:
            QApplication.quit()

    def start_game(self):
        self.auto_move_checkbox.setChecked(False)
        self.auto_move_timer.stop()
        self.moveButton.setEnabled(True)

        if random.choice([0, 1]) == 1:
            self.bot1_turn = True
            self.bot1.side = chess.WHITE
            self.bot2.side = chess.BLACK
            self.bot1_label.setText(f'White: {self.bot1.name}')
            self.bot2_label.setText(f'Black: {self.bot2.name}')
        else:
            self.bot1_turn = False
            self.bot1.side = chess.BLACK
            self.bot2.side = chess.WHITE
            self.bot1_label.setText(f'Black: {self.bot1.name}')
            self.bot2_label.setText(f'White: {self.bot2.name}')

        self.board = chess.Board()
        self.display_board()

    def display_board(self):
        if self.board.is_check():
            # White in check
            if self.board.turn == chess.WHITE: 
                check_square = self.board.king(chess.WHITE)
            else:
                check_square = self.board.king(chess.BLACK)
            svg_data = chess.svg.board(board=self.board, check=check_square).encode('UTF-8')
        else:
            svg_data = chess.svg.board(board=self.board).encode('UTF-8')
        
        self.widgetSvg.load(QByteArray(svg_data))

    def make_move(self):
        if not self.board.is_game_over():
            legal_moves = list(self.board.legal_moves)
            if self.bot1_turn:
                move = self.bot1.get_move(self.board)
            else:
                move = self.bot2.get_move(self.board)

            if move in legal_moves:
                self.moves.append(self.board.san(move))
                self.board.push(move)
                self.bot1_turn = not self.bot1_turn
                self.display_board()
            else: # redo if move was invalid
                print('Invalid move')
                self.make_move()

        else:
            # Stop timer if game over
            self.auto_move_timer.stop()
            self.auto_move_checkbox.setChecked(False)
            
            outcome = self.board.outcome()
            if outcome:
                winner = outcome.winner

                # game is a draw
                if outcome.termination in [chess.Termination.STALEMATE, chess.Termination.INSUFFICIENT_MATERIAL, chess.Termination.THREEFOLD_REPETITION, chess.Termination.FIFTY_MOVES]:
                    self.bot1.draws += 1
                    self.bot2.draws += 1
                    self.display_winner(self.bot1, self.bot2, self.moves, True)

                # bot1 wins
                elif (winner == chess.WHITE and self.bot1.side == chess.WHITE) or (winner == chess.BLACK and self.bot1.side == chess.BLACK):
                    self.bot1.wins += 1
                    self.bot2.losses += 1
                    self.display_winner(self.bot1, self.bot2, self.moves)

                # bot2 wins
                else:
                    self.bot1.losses += 1
                    self.bot2.wins += 1
                    self.display_winner(self.bot2, self.bot1, self.moves)
                
                prompt_recording(self.moves, self.bot1, self.bot2)

app = QApplication([])
bot1, bot2 = RandomBot(), BasicEvalBot()
window = MainWindow(bot1, bot2)

window.show()
app.exec_()


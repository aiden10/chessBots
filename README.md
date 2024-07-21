# Python Interface for chess bots
Makes use of the [python-chess](https://github.com/niklasf/python-chess) library to handle the chess logic

![chessfootage-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/22d53000-3d8f-4201-8daf-ba299b113392)

## Setup
Create a class for your bot with the following properties:
```
class chessBot:
    def __init__():
        self.name = 'Bot'
        self.side = None
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def get_move(self, board): 
        # move calculation logic using the python-chess board
        return move
```
And import into the class with the interface.
```
from Bots.bots import RandomBot, HumanNotBot, BasicEvalBot
app = QApplication([])
bot1, bot2 = RandomBot(), BasicEvalBot()
window = MainWindow(bot1, bot2)

window.show()
app.exec_()
```

## Features
- Recording played games as JSON files with moves in standard algebraic notation 
- Playing large amounts of games with any two bots

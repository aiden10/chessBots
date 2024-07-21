# Interface for chess bots

## About
Provides an easy way to put chess bots against one another using PyQt and the [python-chess](https://github.com/niklasf/python-chess) library to handle the chess logic.

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
Then import the bots and interface.
```
from Interface import Interface
from Bots.bots import RandomBot, BasicEvalBot

bot1, bot2 = RandomBot(), BasicEvalBot()

interface = Interface(bot1, bot2)
interface.start_GUI()
interface.play_games(10)
```

## Features
- Recording played games as JSON files with moves in standard algebraic notation 
- Playing large amounts of games with any two bots

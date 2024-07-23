# Chess Bot Interface

## About
Aims to provide an easy way to put chess bots against one another using PyQt and the [python-chess](https://github.com/niklasf/python-chess) library to handle the chess logic.

![chessfootage-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/22d53000-3d8f-4201-8daf-ba299b113392)

## Setup
Run ```pip install requirements.txt```

Download the ```Interface.py``` file and add it to your project.

Create a bot which contains the following properties: 
- name: string
- side: None
- wins: int (set to 0)
- losses: int (set to 0)
- draws: int (set to 0)

As well as a 'get_move' function which takes in a python-chess board and returns a legal move in UCI format. 

## Examples
### Random Move Bot

```
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
```
### Running the GUI

```
bot1, bot2 = RandomBot(), RandomBot()

interface = Interface(bot1, bot2)
interface.start_GUI()
```

### Running a tournament

```
interface = Interface()

bots = []
for i in range(16):
    new_bot = RandomBot()
    new_bot.name += str(i)
    bots.append(new_bot)

interface.run_knockout(bots)
```

### Playing multiple games

```
interface = Interface()
interface.play_games(100, bot1=RandomBot(), bot2=RandomBot())
```
Or 
```
bot1, bot2 = RandomBot(), RandomBot()

interface = Interface(bot1, bot2)
interface.play_games(100)
```
## Features
- Recording played games as JSON files with moves in standard algebraic notation 
- Playing large amounts of games with any two bots (though still somewhat slow even with multiple threads)
- Auto play
- Running basic knockout tournaments

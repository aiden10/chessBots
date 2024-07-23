from Interface import Interface
from Bots.bots import *

bot1, bot2 = nMoveBasicEvalBot(2), BasicEvalBot()

interface = Interface()
interface.start_GUI()

interface.play_games(100, bot1=RandomBot(), bot2=RandomBot())


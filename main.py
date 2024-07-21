from Interface import Interface
from Bots.bots import RandomBot, BasicEvalBot

bot1, bot2 = RandomBot(), BasicEvalBot()

interface = Interface(bot1, bot2)
interface.start_GUI()
interface.play_games(10)
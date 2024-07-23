from Interface import Interface
from Bots.bots import RandomBot, BasicEvalBot

bot1, bot2 = RandomBot(), BasicEvalBot()

interface = Interface(bot1, bot2)
# interface.start_GUI()
# interface.play_games(100)
bots = []
for i in range(32):
    new_bot = BasicEvalBot()
    new_bot.name += str(i)
    bots.append(new_bot)

interface.run_knockout(bots)
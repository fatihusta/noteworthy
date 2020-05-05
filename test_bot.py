import random
import matrixbz
import procz
import asyncio

@matrixbz.matrixbz_controller(bot_name='dicebot')
class DiceBotController():
    def __init__(self):
        self.name = 'dicebot'

    @matrixbz.matrixbz_method
    def roll(self, start=1, end=6):
        try:
            return random.randint(int(start),int(end))
        except Exception as e:
            return "whoops, don't know how to roll that!"

    @matrixbz.matrixbz_method
    def set_name(self, name):
        self.name = name

    @matrixbz.matrixbz_method
    def say_hello(self):
        return f'howdy, my name is {self.name}!'



manager = procz.ProcManager()
creds = {
    'homeserver': 'https://matrix.decentralabs.io',
    'user': '@bot:decentralabs.io',
    'password': 'hipvegan2019!'
}

print(DiceBotController.MATRIXBZ_BOT_NAME)
bot_generator = lambda: DiceBotController.create_matrix_bot(creds)
bot_generator().run()
# manager.start_proc('dicebot01', bot_generator)
# print('started')

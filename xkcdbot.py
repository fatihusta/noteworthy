import random
import matrixbz
import matrixbz.response as response

@matrixbz.matrixbz_controller(bot_name='xkcdbot')
class DiceBotController():

    AUTH = matrixbz.auth.PublicBot

    @matrixbz.matrixbz_method
    async def lucky(self, context):
        client = context.get('client')
        return response.Image('https://imgs.xkcd.com/comics/preprint.png', client)

    @matrixbz.matrixbz_method
    async def button(self, **kwargs):
        res = random.randint(1,6)
        return response.HTML(f'<h1>test header</h1><button type="button">Click Me!</button>')

creds = {
    'homeserver': 'https://matrix.decentralabs.io',
    'user': '@bot:decentralabs.io',
    'password': 'hipvegan2019!'
}

bot = DiceBotController.create_matrix_bot(creds)
bot.run()

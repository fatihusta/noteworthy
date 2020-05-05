import matrixbz
from noteworthy.notectl.plugins import NoteworthyPlugin

CHANNEL_GREETING = {
    'msgtype': 'm.text',
    'body': 'Heya!'}
}

@matrixbz.matrixbz_controller('welcomebot', channel_greeting=CHANNEL_GREETING)
class WelcomeBotController(NoteworthyPlugin):
    PLUGIN_NAME = 'welcome_bot'

    def __init__(self):
        pass

Controller = WelcomeBotController

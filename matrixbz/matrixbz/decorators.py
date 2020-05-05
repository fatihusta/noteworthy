import functools
from .bot import Bot

def matrixbz_method(func):
    func.matrixbz_method = True
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapped


DEFAULT_GREETING = {
    'msgtype': 'm.text',
    'body': 'Howdy!'
}
def matrixbz_controller(bot_name, channel_greeting=DEFAULT_GREETING):

    def matrixbz_controller_wrapper(cls):
        cls.matrixbz_controller = True
        cls.MATRIXBZ_BOT_NAME = bot_name
        cls.CHANNEL_GREETING = channel_greeting

        @staticmethod
        def create_matrix_bot(creds):
            controller = cls()
            return Bot(controller, creds)
        cls.create_matrix_bot = create_matrix_bot
        return cls
    return matrixbz_controller_wrapper

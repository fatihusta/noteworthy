import functools
from .bot import Bot

def matrixbz_method(func):
    func.matrixbz_method = True
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapped

def matrixbz_msg_handler(func):
    func.matrixbz_msg_handler = True
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapped


def matrixbz_controller(bot_name, channel_greeting=None):

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

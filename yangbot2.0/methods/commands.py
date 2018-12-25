from ..yangbot import YangBot
from ..tools.message_return import message_data

def init(bot):
    @bot.command_on_message
    def catfact(message):
        pass

    @bot.command_on_message
    def register(message):
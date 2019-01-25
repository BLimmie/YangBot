import psycopg2

from src.yangbot import YangBot
from src.tools.message_return import message_data

def init(bot, config):
    pass
    # @bot.auto_on_message(None, None, True)
    # def unsubscribe(message):
    #     if message.content.lower().strip() == "unsubscribe":
    #         pass
    # @bot.auto_on_message(None,None,True)
    # def test(message):
    #     print(message.author.nick)
    #     return message_data(message.channel,message.author.nick)
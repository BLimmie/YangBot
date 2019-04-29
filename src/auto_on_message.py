import psycopg2

from src.tools.message_return import message_data
from src.modules.catfact_helper import get_catfact


def init(bot):
    pass
    @bot.auto_on_message(None, None, True)
    def unsubscribe(message):
        if message.content.lower().strip() == "unsubscribe":
            return message_data(message.channel, get_catfact())
    # @bot.auto_on_message(None,None,True)
    # def test(message):
    #     print(message.author.nick)
    #     return message_data(message.channel,message.author.nick)

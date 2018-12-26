import sys

sys.path.append('..')

from yangbot import YangBot
from tools.message_return import message_data



def init(bot):
    # @bot.auto_on_message(None, None, True)
    # def unsubscribe(message):
    #     if message.content.lower().strip() == "unsubscribe":
    #         pass
    @bot.auto_on_message(None,None,True)
    def test(message):
        return message_data(message.channel,message.content)
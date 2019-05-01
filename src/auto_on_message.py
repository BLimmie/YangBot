import psycopg2
import discord

from src.tools.message_return import message_data
from src.modules.catfact_helper import get_catfact


def init(bot):
    
    @bot.auto_on_message(None, None, True)
    def unsubscribe(message):
        if message.content.lower().strip() == "unsubscribe":
            return message_data(message.channel, get_catfact())

    @bot.auto_on_message(None, None, True)
    def private_message(message):
        if isinstance(message.channel, (discord.DMChannel, discord.GroundChannel)):
            return message_data(message.channel, "I do not reply to private messages. If you have any questions, please message one of the mods.")
        return None
    # @bot.auto_on_message(None,None,True)
    # def test(message):
    #     print(message.author.nick)
    #     return message_data(message.channel,message.author.nick)

import discord

from src.tools.message_return import message_data
from src.modules.catfact_helper import get_catfact
import src.modules.toxicity_helper as toxicity_helper

SUPER_TOXIC_THRESHOLD = .91

def init(bot):

    @bot.auto_on_message(None, None, True)
    def unsubscribe(message):
        if message.content.lower().strip() == "unsubscribe":
            return message_data(message.channel, get_catfact())

    @bot.auto_on_message(None, None, True)
    def private_message(message):
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return message_data(message.channel, "I do not reply to private messages. If you have any questions, please message one of the mods.")
        return None

    async def remove_toxicity(message, score, toxic_message):
        if score > SUPER_TOXIC_THRESHOLD:
            await toxic_message.delete()
            await toxic_message.channel.send("We didn't accept you into this school to be toxic.")

    @bot.auto_on_message(None, None, True, coro=remove_toxicity)
    def check_toxicity(message):
        send_message, score = toxicity_helper.get_toxicity(message)
        return message_data(bot.config["toxic_notif_channel"], send_message, args=[score,message])
    # @bot.auto_on_message(None,None,True)
    # def test(message):
    #     print(message.author.nick)
    #     return message_data(message.channel,message.author.nick)

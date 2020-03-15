import discord
from datetime import timedelta

from src.tools.message_return import message_data
from src.modules.catfact_helper import get_catfact
import src.modules.toxicity_helper as toxicity_helper
from src.modules.repeat_helper import message_author, is_repeat, cycle, flush

BAN_EMOJI_ID = 338384063691751424

def super_toxic_heuristic(scores):
    return False

def init(bot):

    @bot.auto_on_message(None, None, True)
    def unsubscribe(message):
        """
        Extension of $catfact
        """
        if message.content.lower().strip() == "unsubscribe":
            return message_data(message.channel, get_catfact())

    @bot.auto_on_message(None, None, True)
    def private_message(message):
        """
        Yang will respond to private messages with a notice to not message him privately
        """
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return message_data(message.channel, "I do not reply to private messages. If you have any questions, please message one of the mods.")
        return None

    async def remove_toxicity(message, scores, toxic_message):
        if message is None:
            return
        print(message.embed)
        if super_toxic_heuristic(scores):
            await toxic_message.delete()
            await toxic_message.channel.send("We didn't accept you into this school to be toxic.")
        else:
            ban_emoji = await message.guild.fetch_emoji(BAN_EMOJI_ID)
            await message.add_reaction(ban_emoji)
            def check(reaction, user):
                return reaction.message.id == message.id and not user.bot and (reaction.emoji == ban_emoji)

            reaction, user = await bot.client.wait_for("reaction_add", check=check)
            if reaction == ban_emoji:
                try:
                    toxic_message.delete()
                except:
                    await message.channel.send("Message unable to be deleted")

    @bot.auto_on_message(None, None, True, coro=remove_toxicity)
    def check_toxicity(message):
        """
        Notifies admins if a message is toxic (>.83) and removes it if super toxic (>.91)
        """
        send_message, scores = toxicity_helper.get_toxicity(message)
        m = None if send_message is None else ""

        return message_data(bot.config["toxic_notif_channel"], message=m, embed=send_message, args=[scores,message])


    @bot.auto_on_message(None, None, True)
    def mission_complete(message):
        """
        Repeats a message if it has been repeated bot.repeat_n times in a row in a channel
        """
        m_a = message_author(message.content, message.author)
        cycle(bot.repeated_messages_dict[message.channel.id], m_a, bot.repeat_n)
        if is_repeat(bot.repeated_messages_dict[message.channel.id], bot.repeat_n):
            send = bot.repeated_messages_dict[message.channel.id][-1].message
            flush(bot.repeated_messages_dict[message.channel.id])
            return message_data(message.channel, send)
        return None

    # @bot.auto_on_message(timedelta(minutes=1),None,True)
    # def fire(message):
    #     """
    #     fire
    #     """
    #     if "fire" in message.content.lower().split() and "update" in message.content.lower().split():
    #         return message_data(message.channel,"There is no threat to the campus")
    #     return None
    # @bot.auto_on_message(None,None,True)
    # def test(message):
    #     print(message.author.nick)
    #     return message_data(message.channel,message.author.nick)

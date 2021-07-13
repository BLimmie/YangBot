import discord
from datetime import timedelta

from src.tools.bot_function import bot_function
from src.tools.message_return import message_data
from src.modules.catfact_helper import get_catfact
import src.modules.toxicity_helper as toxicity_helper
from src.modules.repeat_helper import message_author, is_repeat, cycle, flush

BAN_EMOJI_ID = 338384063691751424

def super_toxic_heuristic(scores):
    return False

class auto_on_message(bot_function):
    registry = []
    def __init__(self,*args):
        super().__init__(*args)
        auto_on_message.registry.append(self)
    async def action(self,message):
        raise NotImplementedError

class unsubscribe(auto_on_message):
    """
    Extension of $catfact
    """
    def __init__(self):
        super().__init__()
    async def action(self, message):
        if message.content.lower().strip() == "unsubscribe":
            return message_data(message.channel, get_catfact())
# print(help(unsubscribe))

class private_message(auto_on_message):
    """
    Yang will respond to private messages with a notice to not message him privately
    """
    def __init__(self):
        super().__init__()
    async def action(self, message):
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return message_data(message.channel, "I do not reply to private messages. If you have any questions, please message one of the mods.")
        return None

class check_toxicity(auto_on_message):
    """
    Notifies admins if a message is toxic (>.83) and removes it if super toxic (>.91)
    """
    def __init__(self):
        super().__init__()
    async def remove_toxicity(self, message, scores, toxic_message):
        if message is None:
            return
        if super_toxic_heuristic(scores):
            await toxic_message.delete()
            await toxic_message.channel.send("We didn't accept you into this school to be toxic.")
        else:
            ban_emoji = await message.guild.fetch_emoji(BAN_EMOJI_ID)
            await message.add_reaction(ban_emoji)
            def check(reaction, user):
                return reaction.message.id == message.id and not user.bot and (reaction.emoji == ban_emoji)

            reaction, user = await self.bot.client.wait_for("reaction_add", check=check)
            
            try:
                await toxic_message.delete()
            except:
                await message.channel.send("Message unable to be deleted")

    async def action(self, message):
        send_message, scores = toxicity_helper.get_toxicity(message)
        m = None if send_message is None else ""

        toxic_notif_channel = self.bot.client.get_channel(self.bot.config["toxic_notif_channel"])
        t_message = await toxic_notif_channel.send(embed = send_message)
        await self.remove_toxicity(t_message, scores, message)
        return 

class mission_complete(auto_on_message):
    """
    Repeats a message if it has been repeated bot.repeat_n times in a row in a channel
    """
    def __init__(self):
        super().__init__()
    async def action(self, message):
        m_a = message_author(message.content, message.author)
        cycle(self.bot.repeated_messages_dict[message.channel.id], m_a, self.bot.repeat_n)
        if is_repeat(self.bot.repeated_messages_dict[message.channel.id], self.bot.repeat_n):
            send = self.bot.repeated_messages_dict[message.channel.id][-1].message
            flush(self.bot.repeated_messages_dict[message.channel.id])
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

# if __name__ == '__main__':
#     bot = auto_on_message()
#     bot.run()
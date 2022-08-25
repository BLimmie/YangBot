import discord
import markovify
import src.modules.toxicity_helper as toxicity_helper
from src.modules.catfact_helper import get_catfact
from src.modules.repeat_helper import message_author, is_repeat, cycle, flush, message_author_debug
from src.tools.botfunction import BotFunction
from src.tools.message_return import message_data
from src.modules.discord_helper import generate_embed

BAN_EMOJI_ID = 338384063691751424


def super_toxic_heuristic(scores):
    return False


class auto_on_message(BotFunction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message, *args, **kwargs):
        raise NotImplementedError


class unsubscribe(auto_on_message):
    """
    Extension of $catfact
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message, *args, **kwargs):
        if message.content.lower().strip() == "unsubscribe":
            return message_data(message.channel, get_catfact())


# print(help(unsubscribe))

class private_message(auto_on_message):
    """
    Yang will respond to private messages with a notice to not message him privately
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message, *args, **kwargs):
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return message_data(message.channel,
                                "I do not reply to private messages. If you have any questions, please message one of the mods.")
        return None


class check_toxicity(auto_on_message):
    """
    Notifies admins if a message is toxic (>.83) and removes it if super toxic (>.91)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    async def action(self, message, *args, **kwargs):
        send_message, scores = toxicity_helper.get_toxicity(message)
        m = None if send_message is None else ""

        toxic_notif_channel = self.bot.client.get_channel(self.bot.config["toxic_notif_channel"])

        if m is not None:
            toxic_notif_message = await toxic_notif_channel.send(embed=generate_embed(send_message))
            await self.remove_toxicity(toxic_notif_message, scores, message)
        

class mission_complete(auto_on_message):
    """
    Repeats a message if it has been repeated bot.repeat_n times in a row in a channel
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def debug_reset(self):
        self.repeated_messages_dict = {(channel.id):[] for channel in self.bot.channels}

    async def action(self, message, *args, **kwargs):
        m_a = message_author(message.content, message.author, self.bot.debug)
        cycle(self.bot.repeated_messages_dict[message.channel.id], m_a, self.bot.repeat_n)
        if is_repeat(self.bot.repeated_messages_dict[message.channel.id], self.bot.repeat_n):
            send = self.bot.repeated_messages_dict[message.channel.id][-1].message
            flush(self.bot.repeated_messages_dict[message.channel.id])
            return message_data(message.channel, send)
        return None
    
    async def debug_action(self, message, *args, **kwargs):
        m_a = message_author(message.content, message.author, self.bot.debug)
        cycle(self.bot.repeated_messages_dict[message.channel.id], m_a, self.bot.repeat_n)
        if is_repeat(self.bot.repeated_messages_dict[message.channel.id], self.bot.repeat_n):
            send = self.bot.repeated_messages_dict[message.channel.id][-1].message
            flush(self.bot.repeated_messages_dict[message.channel.id])
            return message_data(message.channel, send)       

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

class discord_simulator(auto_on_message):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.BLACKLIST = {1012148524772757605, 372646213096308736, 360265385599303680, 421899094357704704, 498634483910574082, 338237628275097601, 531336865886765057, 839029866128867360, 840809134508474398, 468164570385481729, 991482069265944606, 338238702583021579, 247264977495392258, 495860586244997130, 755204568727420948, 757393586605260921, 676518056872247296, 338237514697408513}
        self.simulator_channel = 1012148524772757605

    async def action(self, message: discord.Message):
        if isinstance(self.simulator_channel, int):
            self.simulator_channel = message.guild.get_channel(self.simulator_channel)
            assert self.simulator_channel is not None, 'Failed to get discord-simulator channel'
        if message.channel.id in self.BLACKLIST: return None

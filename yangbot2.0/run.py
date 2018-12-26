import discord

from yangbot import YangBot
import methods.auto_on_message as auto_on_message
import methods.commands as commands
client = discord.Client()
bot = YangBot(None, client)

auto_on_message.init(bot)
#commands.init(bot)

@client.event
async def on_message(message):
    if not message.author.bot:
        await bot.run_auto_on_message(message)

client.run('')
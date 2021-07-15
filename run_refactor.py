import os
from discord.ext import commands
from src.yangbot import YangBot
import psycopg2
import json

my_secret = os.environ['YB_LOGIN']
bot = commands.Bot(command_prefix='$')
Botter = None
debug = False

config = json.load(open('config.json'))

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

@bot.event
async def on_ready():
    global Botter
    Botter = YangBot(bot, conn, config)
    print('Bot is ready!')

@bot.event
async def on_message(message):
    # Debug Mode on and off
    if message.content == '$debug':
        if Botter.debug is False:
            Botter.debug = True
            await message.channel.send('Debug mode on')
        elif Botter.debug is True:
            Botter.debug = False
            await message.channel.send('Debug mode off')
    # Sigkill in Debug Mode     
    if Botter.debug == True:
        if message.content == '$sigkill':
            await message.channel.send('Killing bot processes...')
            exit()
        # Commands
        if message.content.startswith('$'):
            return_message = await Botter.run_command_on_message(message)
            if return_message is not None:
                channel = return_message.channel
                await channel.send(return_message.message, embed=return_message.embed)
        await Botter.run_auto_on_message(message)
    else:
        # Commands
        if not message.author.bot or message.author.id == 856999058709938177:
            if message.content.startswith('$'):
                return_message = await Botter.run_command_on_message(message)
                if return_message is not None:
                    channel = return_message.channel
                    await channel.send(return_message.message, embed=return_message.embed)
            await Botter.run_auto_on_message(message)

bot.run(my_secret)

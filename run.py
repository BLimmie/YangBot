import discord
from discord.ext import commands
import json
import os
import psycopg2
from src.yangbot import YangBot

bot=None

config = json.load(open('config.json'))

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

intents = discord.Intents().all()
client = commands.Bot('$', intents=intents)
@client.event
async def on_ready():
    global bot
    bot = YangBot(conn, client, config, repeated_messages=5)
    print("Bot is ready")

@client.event
async def on_message(message):
    # Bots cannot call commands EXCEPT TestBot
    if not message.author.bot or message.author.id == 856999058709938177: # TestBot ID
        # Command on Message
        if message.content.startswith('$'):
            return_message = await bot.run_command_on_message(message)
            if return_message is not None:
                await return_message.channel.send(return_message.message, embed=return_message.embed)
        

        # Auto on Message
        return_message2 = await bot.run_auto_on_message(message)
        if return_message2 is not None:
            await return_message2.channel.send(return_message2.message, embed = return_message2.embed)

# Member Join
@client.event
async def on_member_join(member):
    await bot.run_on_member_join(member)

# Member Update
@client.event
async def on_member_update(before, after):
    await bot.run_on_member_update(before, after)

client.run(os.environ['YB_LOGIN'])




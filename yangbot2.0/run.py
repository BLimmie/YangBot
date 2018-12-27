import discord
import json
import os
import psycopg2

from src.yangbot import YangBot
import src.auto_on_message as auto_on_message
import src.commands as commands


config = json.load(open('config.json'))

DATABASE_URL = os.environ['YANGBOT_DB']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

client = discord.Client()
bot = YangBot(cur, client)

auto_on_message.init(bot, config, conn)
commands.init(bot, config, conn)

@client.event
async def on_message(message):
    if message.content.startswith('$'):
        await bot.run_command_on_message(message)
    if not message.author.bot:
        await bot.run_auto_on_message(message)

client.run('')
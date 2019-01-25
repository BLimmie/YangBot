import discord
import json
import os
import psycopg2

from src.yangbot import YangBot
import src.auto_on_message as auto_on_message
import src.commands as commands
import src.on_member_join as omj


config = json.load(open('config.json'))

DATABASE_URL = os.environ['YANGBOT_DB']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

client = discord.Client()
bot = YangBot(conn, client)

auto_on_message.init(bot, config)
commands.init(bot, config)
omj.init(bot, config)


@client.event
async def on_message(message):
    if message.content.startswith('$'):
        await bot.run_command_on_message(message)
    if not message.author.bot:
        await bot.run_auto_on_message(message)

@client.event
async def on_member_join(member):
    await bot.run_on_member_join(member)

client.run(os.environ['YB_LOGIN'])
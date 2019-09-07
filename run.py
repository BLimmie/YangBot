import discord
import json
import os
import psycopg2

from src.yangbot import YangBot
import src.auto_on_message as auto_on_message
import src.commands as commands
import src.member_join as member_join
import src.member_update as member_update
bot=None

config = json.load(open('config.json'))

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

client = discord.Client()
@client.event
async def on_ready():
    global bot
    bot = YangBot(conn, client, config, repeated_messages=5)

    auto_on_message.init(bot)
    commands.init(bot)
    member_join.init(bot)
    member_update.init(bot)
    print("Bot is ready")


@client.event
async def on_message(message):
    if not message.author.bot:
        if message.content.startswith('$'):
            await bot.run_command_on_message(message)
        await bot.run_auto_on_message(message)


@client.event
async def on_member_join(member):
    await bot.run_on_member_join(member)


@client.event
async def on_member_update(before, after):
    await bot.run_on_member_update(before, after)

client.run(os.environ['YB_LOGIN'])

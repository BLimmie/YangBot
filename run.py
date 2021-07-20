import discord
import json
import os
import psycopg2

from src.yangbot import YangBot
bot=None

config = json.load(open('config.json'))

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

client = discord.Client()
@client.event
async def on_ready():
    global bot
    bot = YangBot(conn, client, config)
    print("Bot is ready")


@client.event
async def on_message(message):

    if not message.author.bot or message.author.id == 856999058709938177: # TestBot ID
        if message.content.startswith('$'):            
            return_message = await bot.run_command_on_message(message)
            if return_message is not None:
                channel = return_message.channel
                await channel.send(return_message.message, embed=return_message.embed)
        await bot.run_auto_on_message(message)


@client.event
async def on_member_join(member):
    await bot.run_on_member_join(member)


@client.event
async def on_member_update(before, after):
    await bot.run_on_member_update(before, after)

client.run(os.environ['YB_LOGIN'])



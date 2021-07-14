import os
from discord.ext import commands
from src.yangbot import YangBot
my_secret = os.environ['YB_LOGIN']
bot = commands.Bot(command_prefix='$')
Botter = None
debug = False
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

@bot.event
async def on_ready():
  global Botter
  Botter = YangBot(bot,conn)
  print('Bot is ready!')

@bot.event
async def on_message(message):
  if message.content == '$debug':
    if Botter.debug is False:
      Botter.debug = True
      await message.channel.send('Debug mode on')
    elif Botter.debug is True:
      Botter.debug = False
      await message.channel.send('Debug mode off')
  if Botter.debug == True:
    if message.content == '$sigkill':
      await message.channel.send('Killing bot processes...')
      exit()
    if message.content.startswith('$'):
      return_message = await Botter.run_command_on_message(message)
      if return_message is not None:
        channel = return_message.channel
        await channel.send(return_message.message, embed=return_message.embed)
      await Botter.run_auto_on_message(message)
  else:
    if not message.author.bot:
      if message.content.startswith('$'):
        return_message = await Botter.run_command_on_message(message)
        if return_message is not None:
          channel = return_message.channel
          await channel.send(return_message.message, embed=return_message.embed)
        await Botter.run_auto_on_message(message)

bot.run(my_secret)

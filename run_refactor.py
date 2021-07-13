import os
from discord.ext import commands
from YangBot import YangBot
my_secret = os.environ['TOKEN'] #Needs actual YangBot token
bot = commands.Bot(command_prefix='$')
Botter = None


@bot.event
async def on_ready():
  global Botter
  global bot
  Botter = YangBot(bot)
  print('Bot is ready!')

@bot.event
async def on_message(message):
  if message.content.startswith('$'):
    return_message = await Botter.run_command_on_message(message)
    if return_message is not None:
      channel = return_message.channel
      await channel.send(return_message.message, embed=return_message.embed)
    await Botter.run_auto_on_message(message)

bot.run(my_secret)

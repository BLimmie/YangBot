import os
from discord.ext import commands
from discord.utils import get
import YangBotTests
import discord
my_secret = os.environ['TOKEN2']
channel_id = int(os.environ['CHANNEL_ID'])
bot = commands.Bot(command_prefix=';;')


@bot.event
async def on_ready(m):
  channel = bot.get_channel(channel_id)
  timeout = 0
  while timeout < 5:
    try:
      await channel.send('$ping')
      await bot.wait_for("message",check = lambda message: message.author == await get.user(392801609362440198) and message.content == 'pong!',timeout = 5)
    except:
      timeout+=1
      if timeout == 5:
        return

  testout = '```\nTest Results:\n'
  await m.send('testing...')
  for i in YangBotTests.integration_test.__subclasses__():
    channel = bot.get_channel(channel_id)
    testing = i(bot,channel)
    check = await testing()
    if check == True:
      testout+=('{}:\u2713 \n'.format(i.__name__))
    else:
      testout+=('{}:\u2717 \n'.format(i.__name__))
  testout +='```'
  await m.send(testout)

bot.run(my_secret)
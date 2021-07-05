import os
from discord.ext import commands
import YangBotTests
import asyncio
import discord
my_secret = os.environ['TOKEN2']
channel_id = int(os.environ['CHANNEL_ID'])
bot = commands.Bot(command_prefix=';;')


@bot.event
async def on_ready(m):
  yangBot = bot.get_user_info(392801609362440198)
  timeout = 0
  while yangBot.status != discord.Status.online:
    if timeout < 5:
      await asyncio.sleep(5)
      timeout += 1
    else:
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
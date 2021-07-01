import os
from discord.ext import commands
import YangBotTests
my_secret = os.environ['TOKEN2']
channel_id = int(os.environ['CHANNEL_ID'])
bot = commands.Bot(command_prefix=';;')
@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')


@bot.command(name = 'test')
async def test(m):
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
import os
from discord.ext import commands

my_secret = os.environ['TOKEN2']
channel_id = int(os.environ['CHANNEL_ID'])
bot = commands.Bot(command_prefix=';;')
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


class integration_test():
    def __init__(self):
        self.channel = bot.get_channel(channel_id)
    async def __call__(self):
        if self.message and self.check:
            await self.channel.send(self.message)
            try:
                await bot.wait_for("message",check = self.check(),timeout = 15)
                return True
            except:
                return False
            
class catfact(integration_test):
# tests catfact
    def __init__(self):
        integration_test.__init__(self)
        self.message = '$get_catfact'
    def check(self):
      def m(message):
        return 'test' in message.content
      return m

class choose_empty(integration_test):
# choose command unfilled
  def __init__(self):
    integration_test.__init__(self)
    self.message = '$choose'
  def check(self):
    def m(message):
      return 'Usage:' in message.content
    return m

class choose(integration_test):
# choose command filled
  def __init__(self):
    integration_test.__init__(self)
    self.message = '$choose x;x'
  def check(self):
    def m(message):
      return 'x' in message.description # check this syntax for embeds
    return m

class toxicity_check(integration_test):
  def __init__(self):
    integration_test.__init__(self)
    self.message = 'hey moron'
def check(self):
  def m(message):
    return "Message has been marked for toxicity:" in message.embed.title and message.channel == 421899094357704704
  return m 

@bot.command(name = 'test')
# command to run all integration tests
async def test(m):
  testout = '```\nTest Results:\n'
  await m.send('testing...')
  
  for i in integration_test.__subclasses__():
    testing = i()
    check = await testing()
    if check == True:
      testout+=('{}:\u2713 \n'.format(i().message))
    else:
      testout+=('{}:\u2717 \n'.format(i().message))
  testout +='```'
  await m.send(testout)


bot.run(my_secret)
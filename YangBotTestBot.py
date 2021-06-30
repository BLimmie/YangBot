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

class register_absent(integration_test):
# registering to db w/o existing entry
  def __init__(self):
    integration_test.__init__(self)
    self.message = '$register'
  def check(self):
    def m(message):
      return 'User registered' in message.content
    return m

class register_present(integration_test):
# registering to db w/ existing entry
  def __init__(self):
    integration_test.__init__(self)
    self.message = '$register'
  def check(self):
    def m(message):
      return 'User already registered' in message.content
    return m

class resetregister_present(integration_test):
# resetting db entry w/ existing entry
  def __init__(self):
    integration_test.__init__(self)
    self.message = '$resetregister'
  def check(self):
    def m(message):
      return 'User registration reset' in message.content
    return m

class resetregister_absent(integration_test):
# resetting db entry w/o existing entry
  def __init__(self):
    integration_test.__init__(self)
    self.message = '$resetregister'
  def check(self):
    def m(message):
      return 'User not registered. Use $register to register.' in message.content
    return m

class kickme(integration_test):
# test kick command
  def __init__(self):
    integration_test.__init__(self)
    self.message = '$kickme'
  def check(self):
    def m(message):
      return 'you' in message.content.lower()
    return m

class nickname_empty(integration_test):
# nickname command w/ missing field
  def __init__(self):
    integration_test.__init__(self)
    self.message = '$nickname'
  def check(self):
    def m(message):
      return 'No nickname requested' in message.content
    return m

class nickname_too_long(integration_test):
# nickname command with too long nickname
  def __init__(self):
    integration_test.__init__(self)
    self.message = '$nickname qwertyuiopasdfghjklzxcvbnmqwertyu'
  def check(self):
    def m(message):
      return 'Nickname requested is too long' in message.content
    return m

class send(integration_test):
# testing send command
  def __init__(self):
    integration_test.__init__(self)
    self.message = '$send #dev-testing hello'
  def check(self):
    def m(message):
      return 'hello' in message.content
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
      return 'x' in message.description
    return m

@bot.command(name = 'test')
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
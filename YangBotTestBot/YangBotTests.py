class integration_test():
  async def __call__(self):
      if self.message and self.check:
        await self.channel.send(self.message)
        try:
          await self.bot.wait_for("message",check = self.check(),timeout = 15)
          return True
        except:
         return False

class catfact(integration_test):
# tests catfact
    def __init__(self,bot,channel):
      super().__init__()
      self.bot = bot
      self.channel = channel
      self.message = '$catfact' # the command sent by the testbot
    def check(self):
      def m(message):
        return 'unsubscribe' in message.content # returns T/F depending on Yangbot's return message
      return m 

class choose_empty(integration_test):
# choose command unfilled
  def __init__(self,bot,channel):
    super().__init__()
    self.bot = bot
    self.channel = channel
    self.message = '$choose'
  def check(self):
    def m(message):
      return 'Usage:' in message.content
    return m

class choose_filled(integration_test):
# test choose command filled
  def __init__(self,bot,channel):
    super().__init__()
    self.bot = bot
    self.channel = channel
    self.message = '$choose x; x'
  def check(self):
    def m(message):
      embed = message.embeds[0]
      return 'x' in embed.description
    return m

class toxicity_check(integration_test):
  def __init__(self,bot,channel):
    super().__init__()
    self.bot = bot
    self.channel = channel
    self.message = 'hey moron'
  def check(self):
    def m(message):
      embed = message.embeds[0]
      return "Message has been marked for toxicity:" in embed.title and message.channel == 421899094357704704 # looks for message in toxicity check channel
    return m
  
class register_new(integration_test):
  def __init__(self,bot,channel):
    super().__init__()
    self.bot = bot
    self.channel = channel
    self.message = '$register'
  def check(self):
    def m(message):
      return 'User has been registered' in message.content
    return m

class register_existing(integration_test):
  def __init__(self,bot,channel):
    super().__init__()
    self.bot = bot
    self.channel = channel
    self.message = '$register'
  def check(self):
    def m(message):
      return 'User already registered' in message.content
    return m

class kickme_registered(integration_test):
  def __init__(self,bot,channel):
    self.bot = bot
    self.channel = channel
    self.message = '$kickme'
  def check(self):
    def m(message):
      return 'See you later!' in message.content
    return m

class resetregister_existing(integration_test):
  def __init__(self,bot,channel):
    self.bot = bot
    self.channel = channel
    self.message = '$resetregister'
  def check(self):
    def m(message):
      return 'User registration reset' in message.content
    return m

class resetregister_empty(integration_test):
  def __init__(self,bot,channel):
    self.bot = bot
    self.channel = channel
    self.message = '$resetregister'
  def check(self):
    def m(message):
      return 'User not registered. Use $register to register.' in message.content
    return m

class kickme_unregistered(integration_test):
  def __init__(self,bot,channel):
    self.bot = bot
    self.channel = channel
    self.message = '$kickme'
  def check(self):
    def m(message):
      return "You aren't registered in my memory yet. Please register with $register first" in message.content
    return m


class nickname_empty(integration_test):
  def __init__(self,bot,channel):
    self.bot = bot
    self.channel = channel
    self.message = '$nickname'
  def check(self):
    def m(message):
      return "No nickname requested, usage is $nickname [new nickname]" in message.content
    return m

class nickname_too_long(integration_test):
  def __init__(self,bot,channel):
    self.bot = bot
    self.channel = channel
    self.message = '$nickname abcdefghijklmnopqrstuvwxyz12345678'
  def check(self):
    def m(message):
      return 'Nickname requested is too long' in message.content and message.channel == 531336865886765057
    return m

class nickname(integration_test):
  def __init__(self,bot,channel):
    self.bot = bot
    self.channel = channel
    self.message = '$nickname test'
    def check(self):
      def m(message):
        return "Your nickname request has been submitted" in message.content
      return m

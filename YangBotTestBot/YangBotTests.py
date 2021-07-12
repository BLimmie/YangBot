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
    self.bot = bot
    self.channel = channel
    self.message = '$choose'
  def check(self):
    def m(message):
      print(message.content)
      return 'Usage:' in message.content
    return m

class choose_filled(integration_test):
# test choose command filled
  def __init__(self,bot,channel):
    self.bot = bot
    self.channel = channel
    self.message = '$choose x; x'
  def check(self):
    def m(message):
      embed = message.embeds[0]
      print(embed)
      return 'x' in embed.description
    return m

class toxicity_check(integration_test):
  def __init__(self,bot,channel):
    self.bot = bot
    self.channel = channel
    self.message = 'hey moron'
  def check(self):
    def m(message):
      embed = message.embeds[0]
      return "Message has been marked for toxicity:" in embed.title and message.channel == 421899094357704704
    return m
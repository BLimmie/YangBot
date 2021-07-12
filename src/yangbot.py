import traceback
from src.tools.funcblocker import funcblocker
from commands_refactor import command_on_message



class YangBot():
  def __init__(self,bot):
    self.bot = bot
    self.command_on_message_list = {}
    for action in command_on_message.__subclasses__():
      action.bot = bot
      self.command_on_message_list[action.__name__] = action()
      print(self.command_on_message_list[action.__name__].__dict__)
  async def run_command_on_message(self,message):
    command = message.content.split()[0][1:]
    if command in self.command_on_message_list:
      return await self.command_on_message_list[command].proc(message,message.created_at,message.author)

import traceback
from src.tools.funcblocker import funcblocker
from commands_refactor import command_on_message
from auto_on_message_refactor import auto_on_message


class YangBot():
  def __init__(self,bot,conn):
    self.bot = bot
    self.conn = conn
    self.command_on_message_list = {}
    self.auto_on_message_list = {}
    
    for action in command_on_message.__subclasses__():
      action.bot = bot
      action.conn = conn
      self.command_on_message_list[action.__name__] = action()
    
    for action in auto_on_message.__subclasses__():
        action.bot = bot
        action.conn = conn
        self.auto_on_message_list[action.__name__] = action()
  
  async def run_command_on_message(self,message):
    command = message.content.split()[0][1:]
    if command in self.command_on_message_list:
      return await self.command_on_message_list[command].proc(message,message.created_at,message.author)
  
  async def run_auto_on_message(self,message):
      if message is not None:
          for key, func in self.auto_on_message_list.items():
              try:
                  return await func.proc(message,message.created_at,message.author)
              except Exception:
                  traceback.print_exc()
                  assert False
                  

from datetime import datetime
from _typeshed import Self
import psycopg2
import random
from src.tools.message_return import message_data
from src.modules.db_helper import member_exists, insert_member, refresh_member_in_db
from src.modules.discord_helper import change_nickname, kick_member, try_send
from src.modules.catfact_helper import get_catfact
from src.modules.toxicity_helper import get_toxicity
from src.tools.bot_function import bot_function

class command_on_message(bot_function):
  registry = []
  def __init__(self,*args):
    super().__init__(*args)
    command_on_message.registry.append(self)
  async def action(self,message):
    raise NotImplementedError

class on_member_join(bot_function):
  registry = []
  def __init__(self):
    on_member_join.registery.append(self)
  async def action(self,message):
    raise NotImplementedError

class on_member_update(bot_function):
  registry = []
  def __init__(self):
    on_member_update.registery.append(self)
  def action(self,message):
    raise NotImplementedError

"""
$catfact
Gets random catfact
"""
class catfact(command_on_message):
  def __init__(self):
    super().__init__()
  async def action(self,message):
    return message_data(message.channel, get_catfact())

"""
$register
Registers a user in the db
"""
class register(command_on_message):
  def __init__(self):
    super().__init__()
  async def action(self,message):
    print("Registering")
    user = message.author
    conn = self.conn
    if not member_exists(conn, user.id):
      insert_member(conn, self.bot, user)
    else:
      return message_data(message.channel, "User already registered")
    return message_data(message.channel, "User registered")

"""
$resetregister
Resets the registration in the db in case of bugs
"""
class resetregister(command_on_message):
  def __init__(self):
    super().__init__()
  async def action(self, message):
    user = message.author
    conn = self.conn
    if not member_exists(conn, user.id):
      return message_data(message.channel, "User not registered. Use $register to register.")
    try:
      cur = conn.cursor()
      cur.execute("""DELETE FROM Members WHERE id = '%s' ;""", (user.id,))
      conn.commit()
    except psycopg2.Error as e:
      conn.rollback()
    insert_member(conn, self.bot, user)
    return message_data(message.channel, "User registration reset")

"""
$kickme
kicks an unregistered user???
"""
class kickme(command_on_message):
  def __init__(self):
    super().__init__()
  async def action(self, message):
    conn = self.conn
    if not member_exists(conn, message.author.id):
      return message_data(message.channel, "You aren't registered in my memory yet. Please register with $register first")
    await message.author.send("See you later!")
    await kick_member(message.author)
    return

"""
$nickname [nickname]
Requests to change nickname to [nickname]
Admins click on emoji react to approve/disapprove request
"""
class nickname(command_on_message):
  def __init__(self):
    super().__init__()
  async def nickname_request(self, message, member, new_nickname):
      if new_nickname == None:
        return
      await try_send(member,"Your nickname request has been submitted")
      await message.add_reaction('✅')
      await message.add_reaction('❌')
      def check(reaction, user):
            return reaction.message.id == message.id and not user.bot and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')
      reaction, user = await self.bot.wait_for("reaction_add", check=check)
      if str(reaction.emoji) == '✅':
        try:
          await change_nickname(member, new_nickname)
        except:
          await try_send(member, "Nickname can't be changed")
          return
        await try_send(member, "Your nickname request has been approved")
      else:
        await try_send(member, "Your nickname request has been rejected")

  async def action(self, message):
    user = message.author
    content = message.content
    if len(content.split()) < 2:
      return message_data(message.channel,"No nickname requested, usage is $nickname [new nickname]")
    nickname = " ".join(content.split()[1:])
    if len(nickname) > 32:
      return message_data(message.channel,"Nickname requested is too long")
    requests_channel = self.bot.get_channel(self.bot.config["requests_channel"])
    message = await requests_channel.send("Member {} is requesting a nickname change\nNew nickname: {}".format(user.display_name, nickname))
    await self.nickname_request(message, user, nickname)
    return 



async def remove_message(message, command):
  await command.delete()

"""
$send [channel_mention] [message]
Sends [message] to [channel_mention] and deletes the command to send
"""
class send(command_on_message):
  def __init__(self,rles = [
  bot.config["roles"]["Club Officers"],
  bot.config["roles"]["Admins"],
  bot.config["roles"]["Yangbot Devs"],
  bot.config["roles"]["Server Legacy"]]):
    super().__init__(None, rles, True)
  async def action(self, message):
    content = message.content
    if len(message.channel_mentions) > 0:
      return message_data(
        message.channel_mentions[0],
        content[content.find('>')+1:],
        args=[message]
    )

"""
$choose choice1; choice2[; choice3 ....]
Chooses an option from the list
"""
class choose(command_on_message):
  def __init__(self):
    super().__init__()
  async def action(self, message):
    content = message.content
    l = " ".join(content.split()[1:])
    opts = l.split("; ")
    if len(opts) < 2 or ";" not in content:
      return message_data(message.channel,message= "Usage: `$choose choice1; choice2[; choice3...]`")
    chosen_opt = opts[random.randint(0,len(opts)-1)]
    return message_data(
    message.channel,
    message = "",
    embed = {
      "title": ":thinking:",
      "description": chosen_opt,
      "color": 53380}
      )

import psycopg2
import random
from new_funcblocker import func_decorator
from src.tools.message_return import message_data
from src.modules.db_helper import member_exists, insert_member, refresh_member_in_db
from src.modules.discord_helper import change_nickname, kick_member, try_send
from src.modules.catfact_helper import get_catfact

class bot_function:
  def __init__(self, bot):
    self.bot = bot
  async def __call__(self, *args, **kwargs):
    raise NotImplementedError

class auto_on_message(bot_function):
  async def __call__(self,message,*args,**kwargs):
    return await self.action(message)
  def action(self,message):
    raise NotImplementedError

class command_on_message(bot_function):
  async def __call__(self,message,*args,**kwargs):
    return await self.action(message)
  def action(self,message):
    raise NotImplementedError
@func_decorator()
class catfact(command_on_message):
  async def action(self,message):
    return message_data(message.channel, get_catfact())

@func_decorator()
class register(command_on_message):
  async def action(self,message):
    print("Registering")
    user = message.author
    conn = self.bot.conn
    if not member_exists(conn, user.id):
      insert_member(conn, self.bot, user)
    else:
      return message_data(message.channel, "User already registered")
    return message_data(message.channel, "User registered")
@func_decorator()
class resetregister(command_on_message):
  async def action(self, message):
    user = message.author
    conn = self.bot.conn
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
@func_decorator()
class kickme(command_on_message):
  async def action(self, message):
    conn = self.bot.conn
    if not member_exists(conn, message.author.id):
      return message_data(message.channel, "You aren't registered in my memory yet. Please register with $register first")
    await message.author.send("See you later!")
    await kick_member(message.author)
    return
@func_decorator()
class nickname(command_on_message):
  async def nickname_request(self, message, member, new_nickname):
      if new_nickname == None:
        return
      await try_send(member,"Your nickname request has been submitted")
      await message.add_reaction('✅')
      await message.add_reaction('❌')
      def check(reaction, user):
            return reaction.message.id == message.id and not user.bot and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')
      reaction, user = await self.bot.client.wait_for("reaction_add", check=check)
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
    requests_channel = self.bot.client.get_channel(self.bot.config["requests_channel"])
    message = await requests_channel.send("Member {} is requesting a nickname change\nNew nickname: {}".format(user.display_name, nickname))
    await self.nickname_request(message, user, nickname)
    return 



async def remove_message(message, command):
  await command.delete()

send_roles = [
  bot.config["roles"]["Club Officers"],
  bot.config["roles"]["Admins"],
  bot.config["roles"]["Yangbot Devs"],
  bot.config["roles"]["Server Legacy"]]

@func_decorator(roles = send_roles)
class send(command_on_message):
  async def action(self, message):
    content = message.content
    if len(message.channel_mentions) > 0:
      return message_data(
        message.channel_mentions[0],
        content[content.find('>')+1:],
        args=[message]
    )




class choose(command_on_message):
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
    
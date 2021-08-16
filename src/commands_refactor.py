import random

import psycopg2
import psycopg2.extras
from psycopg2 import sql
from src.modules.catfact_helper import get_catfact
from src.modules.db_helper import member_exists, insert_member, get_table, connection_error
from src.modules.discord_helper import change_nickname, kick_member, try_send
from src.tools.botfunction import BotFunction
from src.tools.message_return import message_data


class command_on_message(BotFunction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message):
        raise NotImplementedError


class catfact(command_on_message):
    """
    $catfact
    Gets random catfact
    """
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    async def action(self, message, *args, **kwargs):
        return message_data(message.channel, get_catfact())
  
class debug(command_on_message):
    """
    $debug
    activates debug mode 
    """
    def __init__(self,*args,**kwargs):
        self.roleslist = ["Admins", "Yangbot Devs", "Server Legacy"]
        super().__init__(roles = self.roleslist, role_whitelist = True, *args, **kwargs)
    
    async def action(self, message, *args, **kwargs):
        if self.bot.debug is False:
            self.bot.debug = True
            await message.channel.send('Debug mode on')
        elif self.bot.debug is True:
            self.bot.debug = False
            await message.channel.send('Debug mode off')

class sigkill(command_on_message):
    """
    $debug
    kills bot processes when in debug mode
    """
    def __init__(self,*args,**kwargs):
        self.roleslist = ["Admins", "Yangbot Devs", "Server Legacy"]
        super().__init__(roles = self.roleslist, role_whitelist = True, *args, **kwargs)
    async def action(self):
      return
    async def debug_action(self, message):
      await message.channel.send('Killing bot processes...')
      exit()


class register(command_on_message):
    """
    $register
    Registers a user in the db
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    async def action(self, message, *args, **kwargs):
        print("Registering")
        user = message.author
        conn = self.bot.conn
        if not member_exists(conn, user.id):
            insert_member(conn, self.bot, user)
        else:
            return message_data(message.channel, "User already registered")
        return message_data(message.channel, "User registered")
    
    async def debug_action(self,message,*args,**kwargs):
        print("Registering")
        user = message.author
        conn = self.bot.conn
        debug = self.bot.debug
        if not member_exists(conn,user,id,debug):
            insert_member(conn,self.bot,user)
        else:
            return message_data(message.channel, "User already registered")
        return message_data(message.channel, "User registered")


class resetregister(command_on_message):
    """
    $resetregister
    Resets the registration in the db in case of bugs
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    async def action(self, message, *args, **kwargs):
        user = message.author
        conn = self.bot.conn
        table = get_table(self.bot.debug)
        if not member_exists(conn, user.id,self.bot.debug):
            return message_data(message.channel, "User not registered. Use $register to register.")
        try:
            cur = conn.cursor()
            cur.execute(sql.SQL("""DELETE FROM {} WHERE id = '%s' ;""").format(sql.Identifier(table)), (user.id,))
            conn.commit()
        except psycopg2.Error as e:
            connection_error(e, conn)
        insert_member(conn, self.bot, user)
        return message_data(message.channel, "User registration reset")


class kickme(command_on_message):
    """
    $kickme
    kicks an unregistered user???
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    async def action(self, message, *args, **kwargs):
        conn = self.bot.conn
        if not member_exists(conn, message.author.id):
            return message_data(message.channel,
                                "You aren't registered in my memory yet. Please register with $register first")
        await message.author.send("See you later!")
        await kick_member(message.author)
        return
    async def debug_action(self, message, *args, **kwargs):
        conn = self.bot.conn
        debug = self.bot.debug
        if not member_exists(conn, message.author.id,debug):
            return message_data(message.channel,
                                "You aren't registered in my memory yet. Please register with $register first")
        await message.author.send("See you later!")
        return



class nickname(command_on_message):
    """
    $nickname [nickname]
    Requests to change nickname to [nickname]
    Admins click on emoji react to approve/disapprove request
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    async def nickname_request(self, message, member, new_nickname):
        if new_nickname == None:
            return
        await try_send(member, "Your nickname request has been submitted")
        await message.add_reaction('✅')
        await message.add_reaction('❌')

        def check(reaction, user):
            return reaction.message.id == message.id and not user.bot and (
                    str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌')

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

    async def action(self, message, *args, **kwargs):
        user = message.author
        content = message.content
        if len(content.split()) < 2:
            return message_data(message.channel, "No nickname requested, usage is $nickname [new nickname]")
        nickname = " ".join(content.split()[1:])
        if len(nickname) > 32:
            return message_data(message.channel, "Nickname requested is too long")
        requests_channel = self.bot.client.get_channel(self.bot.config["requests_channel"])
        message = await requests_channel.send(
            "Member {} is requesting a nickname change\nNew nickname: {}".format(user.display_name, nickname))
        await self.nickname_request(message, user, nickname)
        return


async def remove_message(message, command):
    await command.delete()


class send(command_on_message):
    """
    $send [channel_mention] [message]
    Sends [message] to [channel_mention] and deletes the command to send
    """

    def __init__(self,*args,**kwargs):
        self.roleslist = ["Club Officers", "Admins", "Yangbot Devs", "Server Legacy"]
        super().__init__(roles = self.roleslist, role_whitelist = True, *args, **kwargs)
    async def action(self, message, *args, **kwargs):
        content = message.content
        if len(message.channel_mentions) > 0:
            return message_data(
                message.channel_mentions[0],
                content[content.find('>') + 1:],
                args=[message]
            )


class choose(command_on_message):
    """
    $choose choice1; choice2[; choice3 ....]
    Chooses an option from the list
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    async def action(self, message, *args, **kwargs):
        content = message.content
        l = " ".join(content.split()[1:])
        opts = l.split("; ")
        if len(opts) < 2 or ";" not in content:
            return message_data(message.channel, message="Usage: `$choose choice1; choice2[; choice3...]`")
        chosen_opt = opts[random.randint(0, len(opts) - 1)]
        return message_data(
            message.channel,
            message="",
            embed={
                "title": ":thinking:",
                "description": chosen_opt,
                "color": 53380}
        )

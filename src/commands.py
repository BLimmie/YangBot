import random
from psycopg2 import sql
from src.modules.catfact_helper import get_catfact
from src.modules.db_helper import member_exists, insert_member, get_table, connection_error, dbfunc_run
from src.modules.discord_helper import change_nickname, kick_member, try_send, generate_embed
from src.tools.botfunction import BotFunction
from src.tools.message_return import message_data
from src.modules.state_machines import state, action, machine


class command_on_message(BotFunction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, message):
        raise NotImplementedError

    @staticmethod
    def helptxt():
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

    @staticmethod
    def helptxt():
        return "$catfact \nGets random catfact"
  
class debug(command_on_message):
    """
    $debug

    activates debug mode 
    """
    def __init__(self,*args,**kwargs):
        self.roleslist = ["Admins", "Yangbot Devs", "Server Legacy"]
        super().__init__(roles = self.roleslist, role_whitelist = True, *args, **kwargs)
    
    async def action(self, message, *args, **kwargs):
        for command in self.bot.command_on_message_list.values():
            command.debug_reset()
        for auto in self.bot.auto_on_message_list.values():
            auto.debug_reset()
        for join in self.bot.on_member_join_list.values():
            join.debug_reset()
        for update in self.bot.on_member_update_list.values():
            update.debug_reset()
    
        if self.bot.debug is False:
            self.bot.debug = True
            await message.channel.send('Debug mode on')
        elif self.bot.debug is True:
            self.bot.debug = False
            await message.channel.send('Debug mode off')

    @staticmethod
    def helptxt():
        return "$debug \nActivates debug mode"

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

    @staticmethod
    def helptxt():
        return "$debug \nKills bot processes when in debug mode"


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

    @staticmethod
    def helptxt():
        return "$register \nRegisters a user in the database"


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
        if not member_exists(conn, user.id, self.bot.debug):
            return message_data(message.channel, "User not registered. Use $register to register.")
        cur = conn.cursor()
        db_sql = f"""DELETE FROM {table} WHERE id = {user.id}"""
        dbfunc_run(db_sql, cur, conn)
        conn.commit()
        insert_member(conn, self.bot, user)
        return message_data(message.channel, "User registration reset")

    @staticmethod
    def helptxt():
        return "$resetregister \nResets the registration in the database in case of bugs"


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

    @staticmethod
    def helptxt():
        return "$kickme \nKicks an unregistered user (?)"



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

    @staticmethod
    def helptxt():
        return "$nickname [nickname] \nRequests to change nickname to [nickname]. Requires admin approval."

    

class send(command_on_message):
    """
    $send [channel_mention] [message]

    Sends [message] to [channel_mention] and deletes the command to send
    """

    def __init__(self,*args,**kwargs):
        self.roleslist = ["Club Officers", "Admins", "Yangbot Devs", "Server Legacy"]
        super().__init__(roles = self.roleslist, role_whitelist = True, *args, **kwargs)
    
    async def remove_message(message, command):
        await command.delete()
        
    async def action(self, message, *args, **kwargs):
        content = message.content
        if len(message.channel_mentions) > 0:
            await self.remove_message(message)
            return message_data(
                message.channel_mentions[0],
                content[content.find('>') + 1:],
                args=[message]
            )

    @staticmethod
    def helptxt():
        return "$send [channel] [message] \nSends [message] to [channel]. Must be a channel ping."

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

    @staticmethod
    def helptxt():
        return "$choose choice1; choice2[; choice3; ...] \nChooses an option from the provided list."

class help(command_on_message):
    """
    $help [command]

    Displays description of provided command. If no command is provided, displays all commands
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands_list = {}
        for cmd in command_on_message.__subclasses__():
            self.commands_list[cmd.__name__] = cmd.helptxt()

    async def action(self, message):
        fields = []
        try:
            cmd = message.content[1:].split()[1] # Tries to get the command to search for
        except (IndexError, AttributeError):
            # If no command is given. AttributeError is also catched in case message.content[1:] doesn't return a string.
            for name, desc in self.commands_list.items():
                fields.append({
                    "name": name,
                    "value": desc
                })

        else: # If a command is given
            if cmd in self.commands_list:
                fields.append({
                    "name": cmd,
                    "value": self.commands_list[cmd]
                })
            else: # If no such command exists
                fields.append({
                    "name": "No such command found",
                    "value": "Did you make a typo?"
                })
        return message_data(channel=message.channel, embed={
            "title": "Command List",
            "color": 15920957,
            "fields": fields
        })

    @staticmethod
    def helptxt():
        return "$help [command] \nDisplays description of the provided command. If none is provided, displays description for all commands."

class machine_dual(command_on_message):
    # Here is a demonstration of a machine with two states, with no data.
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    async def action(self, message):

        # Let's define the callbacks for each action, along with the state they'll be put into.

        async def first_state_action(mach: machine, interaction):

            # First we need to specify the new state object

            new_state = state.from_dict(
                embed_dict={ # When interacting with the first button, we want to move into the second state.
                    'title': 'Second State',
                    'description': "I'm the second state in this machine!"
                },
                actions=[
                    action(mach, callback=second_state_action, label='Go back!') # This may seem a bit confusing, but what we're doing is creating the action for the second state, and assigning second_state_action to its callback.
                ]
            )
            await mach.update_state(new_state, interaction) # And we finally update the machine!

        # Similarly with the second state

        async def second_state_action(mach: machine, interaction):

            # First create a new state

            new_state = state.from_dict(
                embed_dict={
                    'title': 'First State',
                    'description': "I'm the first state in this machine!"
                },
                actions=[
                    action(mach, callback=first_state_action, label='Go forward!') # Like before, we set the first state's action to be the first_action.
                ]
            )
            await mach.update_state(new_state, interaction) # And then update the machine!

        # Now let's create the initial state

        initial_state = state.from_dict( 
            embed_dict={
                'title': 'First State',
                'description': "I'm the very first state in this machine!"
            }, 
            actions=[
                action(callback=first_state_action, label="Go forward!") # Since we haven't made our machine yet, it doesn't need to be passed. machine.create() will handle that.
            ]
        )
        await machine.create(initial_state, message) # And finally, create our machine!
        return None

    @staticmethod
    def helptxt():
        return '$machine_dual \nGenerates a sample dual state machine'

class machine_counter(command_on_message):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    # Here is a demonstration of a machine using its data! This machine will count up by 1 everytime a button is pressed.
    async def action(self, message):

        # Let's first define the callback.
        async def take_action(mach: machine, interaction):

            # Since this machine revolves around counting by increments of 1, let's define our new number.
            new_number = mach['count'] + 1 
            # Note that the machine object CAN be treated like a dictionary; mach['count'] is the same as mach.data['count']

            # Now lets create our state object.
            new_state = state.from_dict(
                embed_dict={
                    'title': 'Counter',
                    'description': 'The counter is currently at ' + str(new_number) 
                    # Here we'll make use of our new number! 
                },
                actions=[
                    action(mach, callback=take_action, label='+1') # Since all we're doing is updating by 1, we can use recursion!
                ],
                data={
                    'count': new_number
                }
            )
            await mach.update_state(new_state, interaction) # And now we update the machine!

        # Now let's create the initial state

        initial_state = state.from_dict( 
                embed_dict={
                    'title': 'Counter',
                    'description': 'The counter is currently at 0' # Count starts at 0!
                },
                actions=[
                    action(callback=take_action, label='+1') # As before, we don't have a machine yet, so we don't need to specify it!
                ],
                data={
                    'count': 0
                }
        )
        await machine.create(initial_state, message) # And finally, create our machine!
        return None

    @staticmethod
    def helptxt():
        return '$machine_counter \nCreates a machine capable of counting in increments of 1.'
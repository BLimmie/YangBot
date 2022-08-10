from cProfile import label
from email.message import Message
from pydoc import describe
import random
from datetime import date
from psycopg2 import sql
from src.modules.catfact_helper import get_catfact
from src.modules.db_helper import member_exists, insert_member, get_table, connection_error, dbfunc_run
from src.modules.discord_helper import change_nickname, kick_member, try_send, generate_embed
from src.modules.ucsb_api_helper import get_menus
from src.tools.botfunction import BotFunction
from src.tools.message_return import message_data
from src.tools.state_machines import State, Action, Machine
from discord import ButtonStyle, Interaction
from typing import List


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

class menu(command_on_message):
    def __init__(self, *args, **kwargs):
        self.commons = ['dlg', 'de', 'portola', 'carrillo', 'ortega'] # 'de' is added in case someone searches for 'de la guerra' instead of 'dlg'
        self.mealtimes = ['breakfast', 'lunch', 'dinner', 'brunch']
        self.day = 0 # Force a menu update due to get_menu being asynchronous.
        super().__init__(*args, **kwargs)

    async def action(self, message: Message):
        '''
        Roadmap Idea - Daniel. I've implemented code and pseudo-code for this idea below. This is not final by any means.

        First, check menu. If it is outdated, then update it.
        Second, create some base states and all the actions.
        Third, parse the user's information
        Fourth, using the parsed information, put the machine into the right initial state.
        '''
        message_to_replace = None
        #if date.today().day != self.day: # If the days fail to align, update the menu. It's also important to note *when* the menu gets updated, as this may fail if only day is checked.
        self.menu, self.day = await get_menus()
        #    message_to_replace = await message.channel.send('Please wait while we update the menus...')
        
        homepage = State.from_dict(
            embed_dict={
                'title': 'Home Menu',
                'description': 'Please select one of the dining commons',
                'color': 0x3dc236
            },
            data={
                'position': 'home',
                'mealtime': None
            }
        )

        menu_selector = State.make_template(
            title='{full_commons}',
            description='Please select a menu',
            color=0x9e7402,
            position='{commons}',
            mealtime=None
        )

        meal = State.make_template(
            title='{full_mealtime}',
            description=None,
            mealtime= '{mealtime}'
        )

        # Next, define the base actions and some helper functions
        def process_menu(menu: List) -> str:
            final_string = ''
            for item in menu[:-1]:
                final_string += "·" + item + "\n"
            return final_string + "·" + menu[-1]

        def convert_to_proper(commons: str) -> str:
            match commons:
                case 'dlg':
                    return 'De La Guerra'
                case _:
                    return commons.capitalize()

        def convert_to_improper(commons: str) -> str:
            match commons:
                case 'De La Guerra':
                    return 'dlg'
                case _:
                    return commons.lower()

        @Action.new(label='Back', style=ButtonStyle.gray, row=1)
        async def back(machine: Machine, interaction: Interaction):
            if len(machine.history) < 1: return await interaction.response.send_message("There's nothing to go back to!", ephemeral=True) # It only makes sense to go back when there is at least two states present.
            new_state = machine.history.pop(-1)
            await machine.update_state(new_state, interaction, append_history=False)

        @Action.new(label='Home', style=ButtonStyle.green, row=1)
        async def home(machine: Machine, interaction):
            await machine.update_state(homepage, interaction)

        @Action.new(label='Commons', row=0)
        async def go_to_commons(machine: Machine, interaction, action: Action):
            await machine.update_state(
                State.from_state(menu_selector).format(full_commons=action.label, commons=convert_to_improper(action.label)),
                interaction
            )

        @Action.new(label='Mealtime', row=0)
        async def go_to_meal(machine: Machine, interaction, action: Action):
            working_menu = self.menu[machine['position']][action.label.lower()] # This first goes to the current commons, then grabs the meal.
            new_state = State.from_state(meal).format(full_mealtime=convert_to_proper(machine['position']) + ' ' + action.label, color=0xf2e96b, mealtime=action.label.lower())
            new_state.fields = [
                {
                    'name': station,
                    'value': process_menu(food)
                }
                for station, food in working_menu.items()
            ]
            await machine.update_state(new_state, interaction)  

        # Add the Action buttons to the states now that they've all been defined
        homepage.actions = [
                go_to_commons.copy(label='De La Guerra'), go_to_commons.copy(label='Ortega'), go_to_commons.copy(label='Portola'), go_to_commons.copy(label='Carrillo')
        ]
        menu_selector.actions = [
            go_to_meal.copy(label='Breakfast'), go_to_meal.copy(label='Lunch'), go_to_meal.copy(label='Dinner'), # Update this to be more dynamic
            back, home
        ]
        meal.actions = [back.copy(row=0), home.copy(row=0)]

        # And finally, parse the user's information and determine an initial state
        try:
            # Tries to get the command to search for. Uses a pseudo-auto-fill (so '$menu port' is the same as '$menu portola')
            contents = message.content.lower().split()
            dining_commons = contents[1]
            option = contents[-1] if len(contents) > 2 else None
            for commons in self.commons:
                if commons.startswith(dining_commons):
                    dining_commons = commons if commons != 'de' else 'dlg' # Reassign 'de' alias to 'dlg'
                    break
            else: # If the user input cannot be determined, show homepage
                dining_commons = None
                option = None

            if option and dining_commons: # It only makes sense to have option when dining_commons is valid
                for mealtime in self.mealtimes:
                    if mealtime.startswith(option):
                        option = mealtime
                        break
                else:
                    option = None

        except IndexError:
            # If no argument is specified, then go to homepage
            dining_commons = None
            option = None

        if option:
            match option:
                case 'breakfast':
                    color=0xF2E96B
                case 'brunch':
                    color=0xDEA24E
                case 'lunch':
                    color=0xACBF6D
                case 'dinner':
                    color=0x773738
            initial_state = State.from_state(meal).format(full_mealtime=convert_to_proper(dining_commons) + ' ' + option.capitalize(), color=color, mealtime=option)
            initial_state.fields = [
                {
                    'name': station,
                    'value': process_menu(food)
                }
                for station, food in self.menu[dining_commons][option].items()
            ]
        elif dining_commons:
            initial_state = State.from_state(menu_selector).format(full_commons=convert_to_proper(dining_commons), commons=dining_commons)
        else:
            initial_state = homepage

        await Machine.create(initial_state, message, initial_message='Typing...', message_to_edit=message_to_replace, timeout=10)
        return None

    @staticmethod
    def helptxt():
        return "$menu [dining commons] [mealtime] \nDisplays an interactable Embed showing the menu for the mealtime of the dining commons."

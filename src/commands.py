from cProfile import label
from email.message import Message
from pydoc import describe
import random
from datetime import date
from psycopg2 import sql
from src.modules.catfact_helper import get_catfact
from src.modules.db_helper import member_exists, insert_member, get_table, connection_error, dbfunc_run
from src.modules.discord_helper import change_nickname, kick_member, try_send, generate_embed
from src.modules.ucsb_api_helper import get_allmenusaio
from src.tools.botfunction import BotFunction
from src.tools.message_return import message_data
from src.tools.state_machines import State, Action, Machine
from discord import ButtonStyle, Interaction
from typing import List
from dataclasses import KW_ONLY, dataclass
import asyncio

@dataclass
class help_text:
    '''
    A container for displaying the help text for a command.\n
    It is expected that every class will implement a `helptxt` classmethod and have it return a `help_text` object.
    '''
    name: str
    desc: str
    _: KW_ONLY
    mod_only: bool = False

    def field_dict(self, show_mod_commands: bool) -> dict | None:
        '''
        Returns a field-dictionary for the help text. If this command is mod_only and mod commands shouldn't be displayed, then the field-dict for INVALID_CMD is returned instead.
        '''
        return INVALID_CMD.field_dict(True) if self.mod_only and not show_mod_commands else {
            "name": self.name,
            "value": self.desc
        }

INVALID_CMD = help_text("Command unavailable", "This command is either restricted or doesn't exist.")


class command_on_message(BotFunction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def action(self, _):
        raise NotImplementedError(f'{self.__class__.__name__} failed to implement action.')

    @classmethod
    def helptxt(cls) -> help_text:
        raise NotImplementedError(f'{cls.__name__} failed to implement helptxt.')


class catfact(command_on_message):
    """
    $catfact

    Gets random catfact
    """
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    async def action(self, message, *args, **kwargs):
        return message_data(message.channel, get_catfact())

    @classmethod
    def helptxt(cls):
        return help_text("$catfact", "Gets a random catfact.")
  
class debug(command_on_message):
    """
    $debug

    toggles debug mode 
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

    @classmethod
    def helptxt(cls):
        return help_text("$debug", "Toggles debug mode.", mod_only=True)

class sigkill(command_on_message):
    """
    $sigkill

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

    @classmethod
    def helptxt(cls):
        return help_text("$sigkill", "Kills bot processes when in debug mode.", mod_only=True)


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

    @classmethod
    def helptxt(cls):
        return help_text("$register", "Registers a user in the database.")


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

    @classmethod
    def helptxt(cls):
        return help_text("$resetregister", "Resets the registration in the database in case of bugs")


class kickme(command_on_message):
    """
    $kickme

    kicks a registered user???
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

    @classmethod
    def helptxt(cls):
        return help_text("$kickme", "Kicks you if you are registered in the database.")



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

    @classmethod
    def helptxt(cls):
        return help_text("$nickname [nickname]", "Requests to change nickname to [nickname]. Requires admin approval.")

    

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

    @classmethod
    def helptxt(cls):
        return help_text("$send [channel] [message]",  "Sends [message] to [channel]. Must be a channel ping.", mod_only=True)

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

    @classmethod
    def helptxt(cls):
        return help_text("$choose choice1; choice2[; choice3; ...]", "Chooses an option from the provided list.")

class menu(command_on_message):
    def __init__(self, *args, **kwargs):
        self.commons = ['dlg', 'de-la-guerra', 'portola', 'carrillo', 'ortega'] # 'de' is added in case someone searches for 'de la guerra' instead of 'dlg'
        self.mealtimes = ['breakfast', 'lunch', 'dinner', 'brunch']
        self.date = date.fromisoformat('2000-01-01') # Force a menu update due to get_menu being asynchronous.
        self.updating_menus = False
        self._menu: dict = None
        super().__init__(*args, **kwargs)

    @property
    def menu(self):
        if self._menu is None: raise AttributeError("Menu has not been initialized")
        return self._menu

    @menu.setter
    def menu(self, new_menu):
        self._menu = new_menu

    async def action(self, message):
        '''
        Roadmap Idea - Daniel. I've implemented code and pseudo-code for this idea below. This is not final by any means.

        First, check menu. If it is outdated, then update it.
        Second, create some base states and all the actions.
        Third, parse the user's information
        Fourth, using the parsed information, put the machine into the right initial state.
        '''
        # If the menus are currently being updated, pause execution
        message_to_replace = None
        if self.updating_menus:
            message_to_replace = await message.channel.send('Fetching the menus...')
            while self.updating_menus:
                await asyncio.sleep(1)

        current_date = date.today()
        if current_date != self.date:
            self.updating_menus = True
            message_to_replace = await message.channel.send('Fetching the menus...')
            self.menu, self.date = await get_allmenusaio(current_date.isoformat()), current_date
            self.updating_menus = False
        
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

        def process_menu(menu: List) -> str:
            '''
            Turn a list of food into a usable string.
            '''
            return "\n".join(["**·** " + x for x in menu])

        def convert_to_proper(commons: str) -> str:
            '''
            Convert short-hand code to full name.
            '''
            match commons:
                case 'de-la-guerra':
                    return 'De La Guerra'
                case _:
                    return commons.capitalize()

        def convert_to_improper(commons: str) -> str:
            '''
            Convert full name to short-hand code.
            '''
            match commons:
                case 'De La Guerra':
                    return 'de-la-guerra'
                case _:
                    return commons.lower()

        def determine_common_state(available_meals: dict, *, proper_commons: str | None = None, improper_commons: str | None = None) -> State:
            '''
            Generates a menu_selector for a commons with the correct buttons. If the commons is closed, then it will return a state saying so.
            '''
            proper_commons = proper_commons or convert_to_proper(improper_commons)
            improper_commons = improper_commons or convert_to_improper(proper_commons)

            if available_meals:
                common_state = State.from_state(menu_selector).format(full_commons=proper_commons, commons=improper_commons)
                common_state.actions = [
                    go_to_meal.copy(label=mealtime.capitalize())
                    for mealtime in available_meals
                ] + [back, home]
                return common_state
            else:
                return State.from_dict(
                    embed_dict={
                        'title': proper_commons,
                        'description': 'This dining hall is closed for today.',
                        'color': 0x545454
                    },
                    actions=[
                        back.copy(row=0), home.copy(row=0)
                    ],
                    data={
                        'position': improper_commons,
                        'mealtime': None
                    }
                )

        @Action.new(label='Back', style=ButtonStyle.gray, row=1)
        async def back(machine: Machine, interaction: Interaction):
            # It only makes sense to go back when at least two states have been made.
            if len(machine.history) < 1: return await interaction.response.send_message("There's nothing to go back to!", ephemeral=True) 
            new_state = machine.history.pop(-1)
            await machine.update_state(new_state, interaction, append_history=False)

        @Action.new(label='Home', style=ButtonStyle.green, row=1)
        async def home(machine: Machine, interaction):
            await machine.update_state(homepage, interaction)

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

        @Action.new(label='Commons', row=0)
        async def go_to_commons(machine: Machine, interaction, action: Action):
            commons = action.label
            available_meals = self.menu.get(convert_to_improper(commons), {})
            await machine.update_state(determine_common_state(available_meals, proper_commons=commons), interaction)

        # Add the Action buttons to the states now that they've all been defined (except for menu_selector, which creates its buttons dynamically)
        homepage.actions = [
                go_to_commons.copy(label='De La Guerra', style=ButtonStyle.blurple if 'de-la-guerra' in self.menu else ButtonStyle.gray), 
                go_to_commons.copy(label='Ortega', style=ButtonStyle.blurple if 'ortega' in self.menu else ButtonStyle.gray), 
                go_to_commons.copy(label='Portola', style=ButtonStyle.blurple if 'portola' in self.menu else ButtonStyle.gray), 
                go_to_commons.copy(label='Carrillo', style=ButtonStyle.blurple if 'carrillo' in self.menu else ButtonStyle.gray)
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
                    dining_commons = commons if commons != 'dlg' else 'de-la-guerra' # Reassign 'dlg' alias
                    break
            else:
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

        if not dining_commons: # If the inputs failed to parse, go to homepage
            initial_state = homepage
        elif option in self.menu.get(dining_commons, {}): # Check if option exists in the menu
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
            initial_state.fields = [{
                'name': station,
                'value': process_menu(food)
                }
                for station, food in self.menu[dining_commons][option].items()
            ]
        else: # If it doesn't, attempt to reassign breakfast and lunch to brunch. Finally, since dining_commons is valid, go to its page.
            if option in ('breakfast', 'lunch') and ('brunch' in self.menu.get(dining_commons, {})): # Reassign "breakfast" and "lunch" to "brunch" if neither of the former are being served
                initial_state = State.from_state(meal).format(full_mealtime=convert_to_proper(dining_commons) + ' Brunch', color=0xDEA24E, mealtime='brunch')
                initial_state.fields = [
                    {
                        'name': station,
                        'value': process_menu(food)
                    }
                    for station, food in self.menu[dining_commons]['brunch'].items()
                ]
            else:
                initial_state = determine_common_state(self.menu.get(dining_commons, {}), improper_commons=dining_commons)

        await Machine.create(initial_state, message, initial_message='Typing...', message_to_edit=message_to_replace, timeout=20)
        return None

    @classmethod
    def helptxt(cls):
        return help_text("$menu", "Displays an interactable Embed showing the menu for the mealtime of the dining commons.")

class help(command_on_message):
    """
    $help [command]

    Displays description of provided command. If no command is provided, displays all commands.
    If a command is mod-only, have its helptxt return mod_only_command
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands_list = {
            cmd.__name__: cmd.helptxt()
            for cmd in command_on_message.__subclasses__()
        }

    async def action(self, message):
        fields = []
        show_mod = message.channel.id in self.bot.config['mod_channels']
        try:
            cmd = message.content[1:].split()[1] # Tries to get the command to search for
        except IndexError:
            for helptxt in self.commands_list.values():
                current_field = helptxt.field_dict(show_mod)
                if helptxt.name == current_field['name']:
                    fields.append(current_field)

        else: # If a command is given
            current_field = self.commands_list.get(cmd, INVALID_CMD)
            fields.append(current_field.field_dict(show_mod))

        return message_data(channel=message.channel, embed={
            "title": "Command List",
            "color": 15920957,
            "fields": fields
        })

    @classmethod
    def helptxt(cls):
        return help_text("$help [command]", "Displays description of the provided command. If none is provided, displays description for all commands.")

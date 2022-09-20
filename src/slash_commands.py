import discord
from discord.app_commands import describe
from src.tools.help_text import help_text
from src.tools.events import EventPrompt
from typing import List

class slash_command:
    '''
    A slash command within Discord.
    Slash commands have a few notable distinctions from ordinary commands.\n
    1. They are built into Discord. Ordinary commands are part of YangBot.
    2. They are passed Interactions instead of Messages, and can perform unique responses that ordinary commands can't.
    3. They can be bundled together in 'groups'.
    4. `action` is not expected to return anything, unlike with ordinary commands. Instead, it should close the interaction entirely on its own.
    
    # Methods
      `async action`: The action that will be invoked whenever the command is executed. This will be passed a `Discord.Interaction` object, which should be closed within this coroutine.
      `cls name`: The name of the command. Defaults to the class name. See its docstring.
      `cls description`: The description of the command. Defaults to the helptxt's description. See its docstring.
      `cls helptxt`: A `help_text` object representing the proper display in the help command.

    # Use
    To create a clash command, simply subclass this class and override the methods. Here is an example for a 'ping' command.
    ```python
    class ping(slash_command):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        async def action(self, interaction):
            await interaction.response.send_message("Pong!", ephemeral=True)

        @classmethod
        def helptxt(cls):
            return help_text("/ping", "Replies with 'Pong!'")
    ```
    '''
    _instance = None
    _command_group = None

    def __new__(cls, _):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, bot = None) -> None:
        self.bot = bot

    async def action(self, interaction: discord.Interaction) -> None:
        raise NotImplementedError(f'{self.__class__.__name__!r} failed to implement action method.')

    @classmethod
    def name(cls) -> str:
        '''
        Returns the name of the class.\n
        This is included because there may be scenarios where the command name should not be the same as the class name. 
        An example of this involving groups:
        ```python
        class event_create(slash_command):
            # stuff...
            @classmethod
            def name(cls):
                return 'create'
            
        class timer_create(slash_command):
            # ...
            @classmethod
            def name(cls):
                return 'create'

        class event(slash_command_group): # and a similar one for timer
            subcommands = [event_create]
            description = "Commands relating to events."
        ```
        As a result of the code above, the first command will display as `/event create` instead of `/event event_create`
        '''
        return cls.__name__

    @classmethod
    def description(cls) -> str:
        '''
        Returns the helptxt description\n
        This is useful to override if the Discord description should be different from the `help` command description 
        (e.g short and long description)
        '''
        return cls.helptxt().desc

    @classmethod
    def helptxt(cls) -> help_text:
        raise NotImplementedError(f'{cls.__name__!r} failed to implement helptxt method.')

class slash_command_group:
    '''
    Represents a group for slash commands. An example of a bunch of commands bundled under the 'timer' group
    ```txt
    /timer create
    /timer stop
    /timer pause
    ```
    To implement this in Python (assume `create, stop, pause` are existing `slash_command` objects):
    ```python
    class timer(slash_command_group):
        subcommands = [create, stop, pause]
        description = "Commands relating to managing timers"
    ```
    Both subcommands AND description must be set. A TypeError will be raised if either of these are `None`.
    '''
    subcommands: List[slash_command] = None
    description: str = None

    @classmethod
    def iterator(cls):
        if cls.subcommands is None or cls.description is None: raise NotImplementedError(f"{cls.__name__!r} failed to implement either 'subcommands' or 'description'")
        for cmd in cls.subcommands:
            cmd._command_group = cls
            yield cmd


active_events = {} # A dictionary storage for the active events.

class create_event(slash_command):
    @classmethod
    def name(cls) -> str:
        return 'create'

    @describe(banner='The banner image for the event. This is optional and defaults to nothing.', color='The 6-digit hex code for the color that will be used for the event. Defaults to ff5500.')
    async def action(self, interaction: discord.Interaction, banner: discord.Attachment | None = None, color: str = 'ff5500') -> None:
        if len(color) != 6: return await interaction.response.send_message('Invalid color code provided.')
        try:
            color = int(color, base=16)
        except ValueError:
            return await interaction.response.send_message('Invalid color code provided.')
        await interaction.response.send_modal(
            EventPrompt(
                banner=banner, user_id=interaction.user.id, 
                request_channel=self.bot.client.get_channel(self.bot.config["requests_channel"]), 
                event_channel=self.bot.client.get_channel(self.bot.config['events_channel']),
                color=color
            )
        )

    @classmethod
    def helptxt(cls) -> help_text:
        return help_text('/event create', 'Create a new event in the server.')

class event(slash_command_group):
    subcommands: List[slash_command] = [create_event]
    description: str = 'Commands relating to events.'


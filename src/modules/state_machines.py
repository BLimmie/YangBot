import discord
from discord import Message, TextChannel, ButtonStyle, Emoji, Embed
from discord.ui import View, Button
from discord.ext.commands import Bot
from discord_helper import generate_embed
from typing import List, Coroutine
from copy import deepcopy

# ------------------------------------------------------------------------------------------------------------------------------------------------
#                                                              Beginning of State
# ------------------------------------------------------------------------------------------------------------------------------------------------

class state:
    '''
    An object representing a state for a machine. Behaves like a dictionary for its data, like an object for its embed (see Behavior).

    ## Attributes

    `embed_info`: A dictionary describing attributes for a `discord.Embed` object

    `embed`: A `discord.Embed` object created with `embed_info`.

    `buttons`: A list of `action` objects.

    `data`: Any other data relevant for the machine.
    
    ## Methods

    `@classmethod from_dict`: Creates a state based on the given dictionaries. Performs a shallow copy on all passed parameters.

    `@classmethod from_state`: Creates a new state object from another state. Performs a deepcopy.

    ## Behavior

    This class behaves like a dictionary and object, allowing for keyed and dotted access. 

    `state_obj.key` (dotted access) is equivalent to `state_obj.embed_info[key]`. Setting values behaves similarly.
    
    `state_obj[key]` (keyed access) is equivalent to `state_obj.data[key]`. Setting values behaves similarly.

    `item in state_obj` is equivalent to `item in state_obj.data`.
    '''
    def __init__(self):
        '''
        Initializes a blank state (i.e. all fields are given default values, mostly empty). Default color is white.
        '''
        self.embed_info = {
            "title": None,
            "description": None,
            "color": 16777215,
            "fields": []
        }
        self.buttons = []
        self.data = {}

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value) -> None:
        self.data[key] = value

    def __getattr__(self, key):
        if key in self.embed_info:
            return self.embed_info[key]
        else:
            raise AttributeError(key + " is not a valid Embed attribute.")

    def __setattr__(self, name, value):
        if name in {*self.__dict__.keys(), "embed_info", "buttons", "data"}:
            super().__setattr__(name, value)
        else:
            if name in self.embed_info:
                self.embed_info[name] = value
            else:
                raise AttributeError(name + " is not a valid Embed attribute.")
    
    def __contains__(self, item):
        return item in self.data

    @classmethod
    def from_dict(cls, embed_dict: dict, *, buttons: List[action] = [], data: dict = {}):
        '''
        Creates a state based on the given dictionaries. Performs a shallow copy on all passed parameters.

        ## Parameters

        `embed_dict`: A dictionary with a list of attributes. All keys are optional; any missing keys will be given default values. See attributes of `discord.Embed` for a list of valid key-value pairs.

        `buttons` (Optional): A list of `action` objects. Empty by default.

        `data` (Optional): A dictionary with all relevant data for the machine. Empty by default.
        '''
        self = cls()
        self.embed_info = {
            key: value
            for key, value in embed_dict.items()
            if key in self.embed_info
        }
        self.data = data.copy()
        self.buttons = buttons.copy()
        return self

    @classmethod
    def from_state(cls, other_state: state):
        '''
        Creates a new state object from another state. Performs a deepcopy.

        Please use this method instead of `deepcopy(state)`; deepcopy will fail to generate new buttons.

        ## Parameters

        `other_state`: The state to copy from. Performs a deepcopy on all the attributes. Note that Buttons will be copied, but will not be provided a new action.
        '''
        self = cls()
        self.embed_info = deepcopy(other_state.embed_info)
        self.data = deepcopy(other_state.data)
        # Maybe action can be a subclass for button?
        self.buttons = [
            action(button.machine, callback=button._callback, style=button.style or ButtonStyle.blurple, label=button.label, url=button.url, emoji=button.emoji, row=button.row, disabled=button.disabled)
            for button in other_state.buttons
        ]
        return self

    @property
    def embed(self) -> Embed:
        '''
        A `discord.Embed` object based off the `embed_info` attribute. 
        
        May be reassigned to another `Embed` object; raises a TypeError if assigned to something other than an Embed object.
        '''
        return generate_embed(self.embed_info)

    @embed.setter
    def embed(self, new_embed: Embed):
        if not isinstance(new_embed, Embed): raise TypeError("Invalid object type; Expected Embed, got " + new_embed.__class__.__name__)
        for key, value in new_embed.to_dict().items():
            if key in self.embed_info:
                self.embed_info[key] = value

# ------------------------------------------------------------------------------------------------------------------------------------------------
#                                                              Beginning of Machine
# ------------------------------------------------------------------------------------------------------------------------------------------------

class machine:
    def __init__(self):
        '''
        Please use `machine.create()` to make a new machine, as this will return a blank object.
        '''
        pass
    
    @classmethod
    async def create(cls, client: Bot, initial_state: state, message: Message, * , channel: TextChannel = None, history: List[state] = []):
        '''
        Initializes a machine that may only be modified by and interacted with its creator.
        
        ## Parameters

        `client`: The bot itself.

        `initial_state`: A state object that the machine should put itself into upon creation.

        `message`: The message that initialized the machine.

        `channel` (Optional): The channel that the machine should initialize in. Defaults to `message.channel`.

        `history` (Optional): A history of previous states. Empty by default.
        '''

        # Initialize 'private' variables
        self = cls()
        self._client = client
        self._owner = message.author
        self._message = await channel.send('Initializing...') if channel is not None else await message.channel.send('Initializing...')

        # Initialize 'public' variables
        self.history = history

        # Put the machine into its initial state
        await self.update_state(initial_state)
        return self

    async def update_state(self, new_state: state) -> None:
        '''
        Edits the machine to match the given state.
        '''
        view = View()
        for button in new_state.buttons:
            view.add_item(button)

        self.current_state = new_state
        self._message = await self._message.edit(
            content = None,
            embed=new_state.embed,
            view=view 
        )
        self.data = new_state.data # Should be it a simple reassignment? Or should it loop through the dictionary?
    
    def interaction_check(self, user: discord.User) -> bool:
        '''
        Determines if an interactive is valid. Returns `True` if so, otherwise returns `False`.
        '''
        return user.id == self._owner.id

# ------------------------------------------------------------------------------------------------------------------------------------------------
#                                                              Beginning of Action
# ------------------------------------------------------------------------------------------------------------------------------------------------

async def _DefaultCallback(machine, interaction): # Instead of a print statement, call machine.update_state and change the embed message to the content inside the print statement.
    print('Button was pressed by', interaction.user.name, 'in channel', interaction.channel.name)

class action(Button):
    '''
    An object representing a button within discord. Designed to work with the machine class.

    ## Parameters
    All of the following parameters (except machine) are keyword-only and optional. Unless otherwise specified, all optional parameters default to `None`.

    `machine`: The machine object this button is attached to.

    `callback`: The coroutine that will be invoked when the button is pressed. The action's machine and a `discord.Interaction` object is passed onto this callback as parameters. Defaults to a print statement.

    It is expected that `callback` will generate a state object and call `update_state` onto its passed machine.

    `style`: The style for the button. Defaults to `discord.ButtonStyle.blurple`.

    `label`: The label (text) of the button.

    `emoji`: A `discord.Emoji` object, representing the emoji of the button.

    `row`: The row the button should be placed in, must be between 0 and 4 (inclusive). If this isn't specified, then automatic ordering will be applied.

    `url`: A string representing the url that this button should send to. Note that specifying this changes some functionality (see discord.py docs).

    `disabled`: Whether the button should invoke `callback` whenever pressed. Defaults to `False`.

    ## Attributes

    `machine`: The machine tied to this action.
    '''
    def __init__(self, machine: machine, *, callback: Coroutine=_DefaultCallback , style: ButtonStyle=ButtonStyle.blurple, label: str=None, emoji: Emoji=None, row: int=None, url: str=None, disabled: bool=False):
        super().__init__(style=style, label=label, emoji=emoji, row=row, url=url, disabled=disabled)
        self.machine = machine
        self._callback = callback

    async def callback(self, interaction):
        if self.machine.interaction_check(interaction.user):
            await self._callback(self.machine, interaction)
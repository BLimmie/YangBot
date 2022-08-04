from discord import Message, TextChannel, ButtonStyle, Emoji, Embed, Interaction
from discord.ui import View, Button
from src.modules.discord_helper import generate_embed
from typing import List, Coroutine
from copy import deepcopy
from warnings import warn

# ------------------------------------------------------------------------------------------------------------------------------------------------
#                                                              Beginning of Machine
# ------------------------------------------------------------------------------------------------------------------------------------------------

class YangView(View):
    '''
    A class meant for putting Actions into usable states; discord.py 2.0 requires all buttons be bundled into a 'View' object before passing it onto a message.
    YangView is simply a subclass that is designed to work with machines. 
    
    This class is not intended for use beyond the source code for state machine classes.
    '''
    def __init__(self, machine, actions: List, *, timeout: float = 180):
        if not actions: raise ValueError("List of actions cannot be empty when creating a YangView object")
        super().__init__(timeout=timeout)
        self.machine = machine
        for button in actions:
            if not isinstance(button, Action): raise TypeError("Invalid object given when generating YangView: expected 'action', got " + button.__class__.__name__)
            button.machine = machine
            self.add_item(button)
        self.interaction_check = machine.interaction_check

    async def on_timeout(self) -> None:
        timed_out_state = State()
        timed_out_state.embed_info = self.machine.state.embed_info
        timed_out_state.data = self.machine.state.data
        await self.machine.update_state(timed_out_state)

class Machine:
    '''
    A state machine, represented by an Embed with buttons.
    Machine may be treated like a dictionary, which will return its respective value from its data attribute (in other words, `mach[key]` is equivalent to `mach.data[key]`). The same holds for setting values.
    ## Methods
      `async create`: A coroutine that initializes a new machine. Due to the initializer depending on asynchronous methods, please use `machine.create()` instead of `machine()` to create new instances.
      `async update_state`: A coroutine that updates the machine to match the given state, and closes the given interaction.
      `async interaction_check`: A coroutine that defines the criteria for valid interactions. Default one simply checks if the interaction user is the same as the user who created the machine.
    Note that `interaction_check` is passed an `Interaction` object. If this needs to be replaced, subclass machine and override `interaction_check`.
    ## Attributes
    See the docstring for `machine.create()` for a list of valid initializer parameters.
      `state`: The current state of the machine. May not be reassigned.
      `data`: Any data related to the machine. Note that `mach[key]` is equivalent to `mach.data[key]`. It is not recommended to modify this, as `update_state` will override any existing values.
      `history`: A history of states the machine was in.
    ## Raises
      `TypeError`: 'Button' object given instead of 'action'
      `AttributeError`: Attempting to reassign `machine.state`.
    '''
    def __init__(self):
        '''
        Please use `machine.create()` to make a new machine, as this will return a blank object.
        '''
        pass
    
    @classmethod
    async def create(cls, initial_state, message: Message, * , message_to_edit: Message = None, initial_message: str = 'Initializing...', channel: TextChannel = None, history: List = [], timeout: float = 180, delete_message: bool = False):
        '''
        Initializes a machine that may only be modified by and interacted with its creator.
        ### Parameters
          `initial_state`: A state object that the machine should put itself into upon creation. Note that the machine parameter for all `action` objects of the initial state should be unspecified.
          `message`: The message that initialized the machine.
          `message_to_edit` (Optional): Whether the machine should edit an existing message instead of creating a new one. Sends a new message by default. This parameter is also mutually exclusive with the following two parameters.
          `initial_message` (Optional): The content of the message to send while the machine prepares itself. Defaults to 'Initializing...'
          `channel` (Optional): The channel that the machine should initialize in. Defaults to `message.channel`.
          `history` (Optional): A history of previous states. Defaults to an empty list.
          `timeout` (Optional): A float representing how many seconds of inaction the machine should wait before becoming unusable. Defaults to 180 seconds.
          `delete_message` (Optional): Whether the machine should delete its corresponding message when the machine is deleted (garbage collected). Defaults to `False`.
        '''

        self = cls()
        self._owner = message.author
        if message_to_edit is not None:
            self._message = message_to_edit
        else:
            self._message = await channel.send(initial_message) if channel is not None else await message.channel.send(initial_message)
        self._delete = delete_message
        self._timeout = timeout # For now, timeout is only used for the built-in methods in View. Machine doesn't do any handling with it.

        self.history = history
        self.data = {}

        await self.update_state(initial_state)
        return self

    async def update_state(self, new_state, interaction: Interaction = None) -> None:
        '''
        Edits the machine to match the given state. Data is updated via `dict.update()` and is not outright replaced. In other words, the new state should only include updated data, not all data.

        This method will close the `Interaction` by editing the machine's embed. As such, this should be the last thing called in all `action` objects.

        Calling this method without passing `Interaction` implicitly means that this was not triggered by a user. The only relevant difference is that the `history` attribute will not be updated.
        '''
        view = YangView(self, new_state.actions, timeout=self._timeout) if new_state.actions else None # Check if the action list is non-empty.
        
        if interaction is None:
            self._message = await self._message.edit(
                content=None,
                embed=new_state.embed,
                view=view 
            )
        else:
            self.history.append(self._current_state)
            await interaction.response.edit_message(
                content=None,
                embed=new_state.embed,
                view=view
            )
            self._message = interaction.message
        self.data.update(new_state.data)
        self._current_state = new_state
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        '''
        Determines if an Interaction is valid by returning either `True` or `False`.
        By default, this checks if the user who created the interaction is the same as the user who created the machine. If this needs to be changed, subclass machine and override this.
        '''
        return interaction.user.id == self._owner.id

    @property
    def state(self):
        return self._current_state

    @state.setter # To prevent the changing of this property without using update_state.
    def state(self, new_state):
        raise AttributeError("Can't set state, please use update_state")

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value) -> None:
        self.data[key] = value

    def __del__(self): # To delete the message, if needed.
        if self._delete:
            self._message.delete()

    def __hash__(self) -> int: # Maybe we can use the hash as an identifier, in case ever need this? Maybe useful for machines interacting with each other?
        return hash((self.data, self._current_state, self._owner))

# ------------------------------------------------------------------------------------------------------------------------------------------------
#                                                              Beginning of State
# ------------------------------------------------------------------------------------------------------------------------------------------------

class State:
    '''
    An object representing a state for a machine. Behaves like a dictionary for its data, like an object for its embed (see Behavior).
    ## Attributes
      `embed_info`: A dictionary describing attributes for a `discord.Embed` object
      `embed`: A `discord.Embed` object created with `embed_info`. If you wish to reassign this, please use `update_embed`.
      `actions`: A list of `action` objects.
      `data`: Any other data relevant for the machine.
    ## Methods
      `@classmethod from_dict`: Creates a state based on the given dictionaries. Performs a shallow copy on all passed parameters.
      `@classmethod from_state`: Creates a new state object from another state. Performs a deepcopy.
      `update_embed`: Updates `embed_info` based on the given Embed.
    ## Behavior
    This class behaves like a dictionary and object, allowing for keyed and dotted access. 
      `state_obj.key` (dotted access) is equivalent to `state_obj.embed_info[key]`. Setting values behaves similarly.
      `state_obj[key]` (keyed access) is equivalent to `state_obj.data[key]`. Setting values behaves similarly.
      `item in state_obj` is equivalent to `item in state_obj.data`.
    ## Raises
      `Warning`: Embed_dict passed has a key that isn't in an embed_info
      `TypeError`: `update_embed` was given a non-Embed object.
    '''
    def __init__(self):
        '''
        Initializes a default state, which consists of a basic Embed and empty actions and data. Please use `state.from_dict` (or `from_state`) if you would like the state to be initialized with richer attributes.
        '''
        self.embed_info = {
            'title': 'Default State',
            'description': 'Nothing much to see here!',
            "color": 0xFFFFFF,
            "fields": []
        }
        self.actions = []
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
        if name in {*self.__dict__.keys(), "embed_info", "actions", "data"}:
            super().__setattr__(name, value)
        else:
            if name in self.embed_info:
                self.embed_info[name] = value
            else:
                raise AttributeError(name + " is not a valid Embed attribute.")
    
    def __contains__(self, item):
        return item in self.data

    @classmethod
    def from_dict(cls, embed_dict: dict, *, actions: List = [], data: dict = {}):
        '''
        Creates a state based on the given dictionaries. Performs a shallow copy on all passed parameters.
        ### Parameters
          `embed_dict`: A dictionary with a list of attributes. All keys are optional; any missing keys will be given default values. See attributes of `discord.Embed` for a list of valid key-value pairs.
          `actions` (Optional): A list of `action` objects. Empty by default.
          `data` (Optional): A dictionary with all relevant data for the machine. Empty by default.
        '''
        self = cls()

        for key, item in embed_dict.items():
            if key not in self.embed_info:
                warn("Invalid embed_dict attribute " + key + " given")
            else:
                self.embed_info[key] = item

        self.data = data.copy()
        self.actions = actions.copy()
        return self

    @classmethod
    def from_state(cls, other_state, *, machine: Machine = None):
        '''
        Creates a new state object from another state. Performs a deepcopy.
        ### Parameters
          `other_state`: The state to copy from.
          `machine` (Optional): The machine that each `action` should be assigned to. Defaults to the machine attribute of each `action`.
        '''
        self = cls()
        self.embed_info = deepcopy(other_state.embed_info)
        self.data = deepcopy(other_state.data)
        self.actions = [
            Action(machine or button.machine, callback=button._callback, style=button.style or ButtonStyle.blurple, label=button.label, url=button.url, emoji=button.emoji, row=button.row, disabled=button.disabled)
            for button in other_state.actions
        ]
        return self

    @property
    def embed(self) -> Embed:
        '''
        A `discord.Embed` object based off the `embed_info` attribute. Please use `update_embed` if you wish to reassign this state's embed
        '''
        return generate_embed(self.embed_info)

    @embed.setter
    def embed(self, new_embed: Embed):
        warn('Please use the update_embed method to change a state\'s embed')

    def update_embed(self, new_embed: Embed):
        '''
        Updates `embed_info` based on the given Embed object. Raises a TypeError if given something other than an Embed, and prints a warning for any invalid keys given.
        '''
        if not isinstance(new_embed, Embed): raise TypeError("Invalid object type; Expected Embed, got " + new_embed.__class__.__name__)
        for key, value in new_embed.to_dict().items():
            if key in self.embed_info:
                self.embed_info[key] = value
            else:
                warn("Invalid embed_dict attribute " + key + " given")

# ------------------------------------------------------------------------------------------------------------------------------------------------
#                                                              Beginning of Action
# ------------------------------------------------------------------------------------------------------------------------------------------------

async def DefaultCallback(mach: Machine, interaction: Interaction):
    await mach.update_state(State(), interaction)

class Action(Button):
    '''
    An object representing a button within discord. Designed to work with the machine class.
    ## Parameters and Attributes
    All of the following parameters are keyword-only and optional. Unless otherwise specified, all parameters default to `None`. 
    Every parameter (except callback) is also an equivalently named attribute.
      `callback`: The coroutine that will be invoked when the button is pressed. It will be executed as `callback(machine, interaction)`, where interaction is a `discord.Interaction` object. Defaults to changing to a generic state.
       It is expected that `callback` will generate a state object and call `update_state` onto its passed machine.
      `style`: The style for the button. Defaults to `ButtonStyle.blurple`.
      `label`: The label (text) of the button.
      `emoji`: A `discord.Emoji` object, representing the emoji of the button.
      `row`: The row the button should be placed in, must be between 0 and 4 (inclusive). If this isn't specified, then automatic ordering will be applied.
      `url`: A string representing the url that this button should send to. Note that specifying this changes some functionality (see discord.py docs).
      `disabled`: Whether the button should invoke `callback` whenever pressed. Defaults to `False`.
    There is an additional attribute, `machine`, that refers to the machine that the button is currently attached to. This is not a parameter and should not be modified.
    ## Methods
      `clone`: Returns a copy of the button.
    `action`: A decorator that provides an alternate way to construct Action objects. For example:
    ```
    @Action.action(label='Click me!')
    async def do_something(machine, interaction):
        print('I was pressed!')
    ```
    This is the same as 
    ```
    do_something = Action(label='Click me!', callback=do_something)
    ```
    Note that the variable for the coroutine is reassigned to an Action object.
    '''
    def __init__(self, *, callback: Coroutine=DefaultCallback , style: ButtonStyle=ButtonStyle.blurple, label: str=None, emoji: Emoji=None, row: int=None, url: str=None, disabled: bool=False):
        super().__init__(style=style, label=label, emoji=emoji, row=row, url=url, disabled=disabled)
        self.machine = None
        self._callback = callback

    async def callback(self, interaction):
        await self._callback(self.machine, interaction)

    @classmethod
    def action(cls, **kwargs):
        '''
        A decorator used to be able to construct Action objects more easily. Sample use:
        ```
        @Action.action(label='Click me!')
        async def do_something(machine, interaction):
            print('I was pressed!')
        ```
        This is equivalent to `do_something = Action(label='Click me!', callback=do_something)`. Note that the variable for the coroutine is reassigned to an Action object.
        '''
        def wrap(callback):
            return cls(callback=callback, **kwargs)

        return wrap

    def clone(self):
        '''
        Returns a copy of this Action.
        '''
        return type(self)(callback=self._callback, style=self.style, label=self.label, emoji=self.emoji, row=self.row, url=self.url, disabled=self.disabled)

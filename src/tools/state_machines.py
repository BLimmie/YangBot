from discord import Message, TextChannel, ButtonStyle, Emoji, Embed, Interaction, InteractionResponded
from discord.ui import View, Button
from discord.ext.commands import Context
from src.modules.discord_helper import generate_embed
from typing import List, Coroutine
from types import NoneType
from copy import deepcopy
from warnings import warn
from inspect import signature

_EMPTY_LIST = [] 
_EMPTY_DICT = {}
# to work around parameters w/ default values without having to default to None

# ------------------------------------------------------------------------------------------------------------------------------------------------
#                                                              Beginning of Machine
# ------------------------------------------------------------------------------------------------------------------------------------------------

class _MachineView(View):
    '''
    A class meant for putting Actions into usable states; discord.py 2.0 requires all buttons be bundled into a 'View' object before passing it onto a message.
    MachineView is simply a subclass that is designed to work with machines. 
    
    This class is intended to be private, and its use is not recommended beyond the methods within the state machine classes.
    '''
    def __init__(self, machine, actions: List, *, timeout: float = 180):
        if not actions: raise ValueError("List of actions cannot be empty when creating a MachineView object")
        super().__init__(timeout=timeout)
        self.machine: Machine = machine
        for button in actions:
            if not isinstance(button, Action): raise TypeError(f"Invalid object given: expected 'Action', got {button.__class__.__name__}")
            button.machine = machine
            self.add_item(button)

    async def on_timeout(self) -> None: 
        await self.machine.on_timeout()

    async def interaction_check(self, interaction: Interaction) -> bool:
        return await self.machine.interaction_check(interaction)

class Machine:
    '''
    A state machine, represented by an Embed with buttons.
    Machine may be treated like a dictionary, which will return its respective value from its data attribute (in other words, `mach[key]` is equivalent to `mach.data[key]`). The same holds for setting values.\n
    ## Methods\n
      `async create`: A coroutine that initializes a new machine. 
      Due to the initializer depending on asynchronous methods, please use `machine.create()` instead of `machine()` to create new instances.\n
      `async update_state`: A coroutine that updates the machine to match the given state, and closes the given interaction.\n
      `async interaction_check`: The coroutine that determines the validity of an interaction. Defaults to checking if the user is in the machine's whitelist.\n
      `async on_timeout`: The coroutine that is called whenever the machine times out. Defaults to removing buttons.\n
       See the Subclassing category for more information on the two aforementioned methods.\n
    ## Attributes\n
    See the docstring for `Machine.create()` for a list of valid initializer parameters.
      `state`: The current state of the machine. May not be reassigned.\n
      `data`: Any data related to the machine. Note that `mach[key]` is equivalent to `mach.data[key]`. 
      It is not recommended to modify this, as `update_state` may override any existing values.\n
      `history`: A history of states the machine was in. If this attribute is set to `None`, then a history will not be tracked.\n
      `whitelist`: A list of User IDs that may interact with this machine. 
      This may also be `None`, which indicates that any user may interact. See the subclassing category.\n
      `active`: Whether the machine has Actions that can be interacted with. If every action is disabled, then this is False. May not be reassigned.\n
    ## Subclassing\n
    The following two methods are designed to be overridden.
    ### interaction_check
    This returns `True` if the interacting user is in the whitelist, otherwise `False`.
    Note that the `whitelist` attribute is only ever accessed here. If you override this method, then also consider the `whitelist` parameter in `Machine.create` as overridden (i.e. it can be anything you want).\n
    Override this method like so
    ```python
    async def interaction_check(self, interaction: Interaction) -> bool:
        # check if interaction.user matches self.whitelist
        return True/False
    ```
    ### on_timeout
    This method is called once the timeout period is elapsed.\n
    The default one updates the machine's state by removing any existing actions. Override this method like so
    ```python
    async def on_timeout(self) -> None:
        timed_out_state = State()
        # do stuff
        await self.update_state(timed_out_state)
    ```
    ## Raises\n
      `TypeError`: 'Button' object given instead of 'Action'
      `AttributeError`: Attempting to reassign `state` or `active` parameters.
    '''
    def __init__(self):
        '''
        Please use `Machine.create()` to make a new machine, as this will return a blank object.
        '''
        pass
    
    @classmethod
    async def create(cls, 
        initial_state, 
        msg_or_interaction: Message | Interaction | Context | None = None, 
        *,
        whitelist: List[int] | None = _EMPTY_LIST, 
        initial_message: str = 'Initializing...', 
        message_to_edit: Message | None = None, 
        channel: TextChannel | None = None, 
        history: List | None = _EMPTY_LIST, 
        timeout: float = 180,
        delete_message: bool = False
    ):
        '''
        Initializes a machine that may only be modified by and interacted with its creator.\n
        ### Parameters\n
          `initial_state`: A state object that the machine should put itself into upon creation.\n
          `msg_or_interaction = None`: The message/interaction that initialized the machine (from a user). Context objects are also supported.
           This parameter will be ignored if `message_to_edit/channel` and `whitelist` are given, and as such may be omitted.\n
          **The following parameters are keyword only**.\n
          `whitelist = [msg_or_interaction.user.id]`: A list containing all the valid user IDs that may interact with this machine. Passing `None` to this parameter allows interaction from any user. 
           Note that this parameter is only used in `interaction_check`. If you override `interaction_check`, then this may be assigned to anything.\n
          `initial_message = 'Initializing...'`: The content of the message to send while the machine prepares itself. 
           This parameter is ignored if `message_to_edit` is given.\n
          `message_to_edit = None`: The message that the machine should attach itself to. Sends a new message by default. Mutually exclusive with `channel`.\n
          `channel = msg_or_interaction.channel`: The channel that the machine should initialize in. Mutually exclusive with `message_to_edit`.\n
          `history = []`: A history of previous states. Pass `None` to this parameter if you don't want the machine to track its history.\n
          `timeout = 180`: A float representing how many seconds of inaction the machine should wait before becoming unusable.\n
          `delete_message = False`: Whether the machine should delete its corresponding message when the machine is deleted (garbage collected).\n
        ### Rasies\n
        `ValueError`: `message_to_edit` is given alongside `channel`.
        '''
        if message_to_edit and channel: raise ValueError("message_to_edit parameter is mutually exclusive with channel")

        self = cls()
        if message_to_edit is not None:
            self.__message = message_to_edit
        else:
            if channel is not None:
                self.__message = await channel.send(initial_message) 
            elif isinstance(msg_or_interaction, (Message, Context)):
                self.__message = await msg_or_interaction.channel.send(initial_message)
            else:
                try:
                    await msg_or_interaction.response.send_message(initial_message)
                except InteractionResponded:
                    pass
                finally:
                    self.__message = await msg_or_interaction.original_message()

        self._delete = delete_message
        self._timeout = timeout # For now, timeout is only used for the built-in methods in View. Machine doesn't do any handling with it.
        self.__recent_view = None
        
        self.history: List | None = [] if history is _EMPTY_LIST else None
        if whitelist is _EMPTY_LIST:
            self.whitelist: List[int] = [msg_or_interaction.author.id if isinstance(msg_or_interaction, (Message, Context)) else msg_or_interaction.user.id]
        else:
            self.whitelist = whitelist
        self.data = {}

        return await self.update_state(initial_state, append_history=False)

    async def update_state(self, new_state, interaction: Interaction | None = None, *, append_history: bool = True, replace_data: bool = False):
        '''
        Edits the machine to match the given state. The current machine is returned to allow for fluent-style chaining.\n
        ### Parameters\n
          `new_state`: The state to update to. The machine will update its own attributes based on the attributes of `new_state`.\n
          `interaction = None`: An Interaction object, usually provided by an Action's callback. 
          This method will close the `Interaction` by editing the machine's embed. As such, this should be the last thing called in all `Action` objects. 
          Passing an Interaction object is not required to use this method though.\n
          **The following parameters are keyword only**\n
          `append_history = True`: By default, this method will always add the most recent state to the machine's history (if the history attribute is not `None`). 
          If this needs to be avoided, set this parameter to `False`.\n
          `replace_data = False`: Data is updated via `dict.update()` and is not outright replaced. 
          If you would like to replace the machine's data dictionary outright (set it to a new dictionary), set this to `True`. 
        '''
        if self.__recent_view is not None: self.__recent_view.stop()
        view = _MachineView(self, new_state.actions, timeout=self._timeout) if new_state.actions else None # Check if the action list is non-empty.

        if interaction is None:
            self.__message = await self.__message.edit(
                content=None,
                embed=new_state.embed,
                view=view 
            )
        else:
            await interaction.response.edit_message(
                content=None,
                embed=new_state.embed,
                view=view
            )
            self.__message = await interaction.original_message()
        if replace_data:
            self.data = new_state.data
        else:
            self.data.update(new_state.data)
        if append_history and self.history is not None:
            self.history.append(self.__current_state)

        self.__current_state: State = new_state
        self.__recent_view = view
        return self
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        '''
        Determines if an Interaction is valid by returning either `True` or `False`.\n
        By default, this checks if the user who interacted is in the whitelist. If this needs to be changed, subclass Machine and override this.
        '''
        if self.whitelist is None:
            return True
        return interaction.user.id in self.whitelist

    async def on_timeout(self) -> None:
        '''
        The coroutine to be executed when the machine times out. This method is not passed any additional parameters.\n
        By default, this removes the buttons on the machine. If this needs to be changed, subclass Machine and override this.
        '''
        timed_out_state = State.from_dict(
            embed_dict = self.state.embed_info,
            data = self.state.data
        )
        await self.update_state(timed_out_state, append_history=False)

    @property
    def state(self):
        return self.__current_state

    @state.setter # To prevent the changing of this property without using update_state.
    def state(self, _):
        raise AttributeError("Can't set state, please use update_state")

    @property
    def active(self) -> bool:
        '''
        `True` if this machine has any active buttons, `False` if all buttons are disabled, or if there are no buttons to interact with.
        '''
        total_buttons = len(self.state.actions)
        inactive_buttons = 0
        if total_buttons == 0: return False
        for action in self.state.actions:
            if action.disabled:
                inactive_buttons += 1
        return total_buttons != inactive_buttons

    @active.setter
    def active(self, _):
        raise AttributeError("Can't set active attribute.")

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value) -> None:
        self.data[key] = value

    def __del__(self): # To delete the message, if needed.
        if self._delete:
            self.__message.delete()

    def __hash__(self) -> int: # Maybe we can use the hash as an identifier, in case ever need this? Maybe useful for machines interacting with each other?
        return hash((self.data, self.__current_state, self.whitelist))

# ------------------------------------------------------------------------------------------------------------------------------------------------
#                                                              Beginning of State
# ------------------------------------------------------------------------------------------------------------------------------------------------

class State:
    '''
    An object representing a state for a machine. Behaves like a dictionary for its data, like an object for its embed (see Behavior). 
    Most methods also support fluent-style and method chanining, and its use is highly encouraged.\n
    ## Attributes\n
      `embed_info`: A dictionary describing attributes for a `discord.Embed` object. It includes most attributes for Embed.\n
      `embed`: A `discord.Embed` object created with `embed_info`. If you wish to set this to an existing Embed, use `set_embed`.\n
      `actions`: A list of `Action` objects.\n
      `data`: Any other data relevant for the machine.\n
      `VALID_EMBED_KEYS`: A set of all the valid keys for `embed_info`. This is a class attribute so it may be accessed directly from State.\n
       This contains the following (along with type requirements):
    ```python
    str: title, description, url, image, thumbnail
    int: color
    dict: author, footer
    List[dict]: fields
    datetime: timestamp
    ```
    ## Methods\n
    Unless otherwise stated in its docstring, all methods (except class methods) return the current state to allow for fluent-style chaining.
      `@cls from_dict`: Creates a state based on the given dictionaries. Performs a shallow copy on all passed parameters.\n
      `@cls from_state`: Creates a new state object from another state. Performs a deepcopy on `embed_info` and `data`, and performs a shallow copy on each Action object.\n
      `@cls make_template`: Generates a template state, one designed to work with `State.format()`. This is useful for making a base state that other states will be derived from.\n
      `update_embed_info`: Updates `embed_info` based on the given Embed.\n
      `set_embed`: Sets the `embed` attribute to the given embed. The state will use this instead of `embed_info`.\n
      `format`: Loops through `embed_info` and `data`, and performs `string.format(**kwargs)` on all string values. Can also reassign types (see docstring).\n
      `add_action`: Adds the given Actions to the state.\n
      `remove_action`: Removes the given Actions from the state\n
      `removes_all_actions`: Removes every Action from the state.\n
    ## Behavior\n
    This class has behavior allowing for convenient setting and retrieval. The following statements are equivalent.
    ```python
    state.key == state.embed_info[key]
    state[key] == state.data[key]
    item in state == item in state.data
    ```
    These may be used for both getting and setting.\n
    ## Raises\n
      `Warning`: `embed_dict` parameter for `from_dict` has an invalid/unsupported Embed key.
      `TypeError`: `update_embed_info, set_embed, add_action, remove_action` given inappropriate types (see their docstrings).
      `ValueError`: Action given for `remove_action` is not present.
    '''
    VALID_EMBED_KEYS = {'author', 'color', 'title', 'description', 'fields', 'footer', 'image', 'thumbnail', 'timestamp'} # Add more memebers here as embed_info grows

    def __init__(self):
        '''
        Initializes a default state, which consists of a basic Embed and empty actions and data. Please use one of State's classmethods to initialize a richer state.
        '''
        self.embed_info = {
            'author': None,
            'color': 0xFFFFFF,
            'title': 'Default State',
            'description': 'Nothing much to see here!',
            'fields': [],
            'footer': None,
            'image': None,
            'thumbnail': None
        }
        self.actions = []
        self.data = {}
        self._embed = None

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value) -> None:
        self.data[key] = value

    def __getattr__(self, key):
        try:
            return self.embed_info[key]
        except KeyError:
            raise AttributeError("Invalid embed_info key given: " + key)

    def __setattr__(self, name, value):
        if name in self.VALID_EMBED_KEYS:
            self.embed_info[name] = value
        else:
            super().__setattr__(name, value)
    
    def __contains__(self, item):
        return item in self.data

    @classmethod
    def from_dict(cls, embed_dict: dict, *, actions: List = _EMPTY_LIST, data: dict = _EMPTY_DICT):
        '''
        Creates a state based on the given dictionaries. Performs a shallow copy on all passed parameters.\n
        If `embed_dict` has an invalid/unsupported key, then a warning will be printed.
        ### Parameters
          `embed_dict`: A dictionary describing an Emed. 
          All keys are optional; any missing keys will be given default values. 
          See the docstring for `State` (attribute `VALID_EMBED_KEYS`) for a list of acceptable keys and their type requirements.
          `actions = []`: A list of `action` objects.
          `data = {}`: A dictionary with all relevant data for the machine.
        '''
        self = cls()

        for key, item in embed_dict.items():
            if key not in self.VALID_EMBED_KEYS:
                warn("Invalid embed_dict attribute " + key + " given")
            else:
                self.embed_info[key] = item

        self.data = data.copy() if data is not _EMPTY_DICT else {}
        self.actions = actions.copy() if actions is not _EMPTY_LIST else []
        return self

    @classmethod
    def from_state(cls, other_state):
        '''
        Creates a new state object from another state. 
        Performs a deepcopy on `embed_info` and `data`; a shallow copy on every `Action` object and the other state's Embed attribute (if it has been set).
        '''
        self = cls()
        self.embed_info = deepcopy(other_state.embed_info)
        self.data = deepcopy(other_state.data)
        self.actions = [
            button.copy()
            for button in other_state.actions
        ]
        self._embed = other_state._embed
        return self

    @classmethod
    def make_template(cls, *, author: dict = '#author', color: int = '#color', title: str='#title', description: str='#description', fields: List[dict]='#fields', footer: dict = '#footer', image: str = '#image', thumbnail: str = '#thumbnail', actions: List=_EMPTY_LIST, **kwargs):
        '''
        Generates a template state, one designed to work with `State.format()`. This is meant for making a base state that other states will be derived from.\n
        By default, State.format will reassign everything it operates on to a string value. 
        If this becomes an issue and needs to be assigned to another data type, then pass the argument as `key='#key'`. 
        For example, to ensure that color is assigned an int, you can pass it as `color='#color'`.\n
        This method only accepts keyword arguments. Every explicitly defined keyword arg (except actions) will be passed to `embed_info`, actions will be passed to `actions`, and everything else will be passed to `data`.
        '''
        self = cls()
        self.embed_info = {
            'author': author,
            'color': color,
            'title': title,
            'description': description,
            'fields': fields,
            'footer': footer,
            'image': image,
            'thumbnail': thumbnail
        }
        self.actions = actions if actions is not _EMPTY_LIST else []
        for key, value in kwargs.items():
            self[key] = value
        return self

    def format(self, **kwargs):
        '''
        Recursively loops through `embed_info`, `data`, and their `List/dict` elements, and performs `str.format(**kwargs)` on all string values. This method only accepts keyworded arguments.\n
        Any (dictionary) key with an associated string value of '#key' will not be assigned to a string. Instead, it will be assigned to the parameter it is given in kwargs (or `None` if it is not present). To give an example of this:
        ```python
        >>> base_state = State.make_template(color='#color')
        ... print(type(base_state.color))
        <class 'str'>
        >>> new_state = State.from_state(base_state).format(color=0xFFFFFF) # passed as an int
        ... print(type(new_state.color))
        <class 'int'>
        ```
        If color wasn't passed into format in the above example, then it would have been assigned to `None` instead.\n
        '''
        def recursive_list(L: list):
            for i in range(len(L)):
                item = L[i]
                if isinstance(item, str):
                    L[i] = item.format(**kwargs)
                elif isinstance(item, list):
                    recursive_list(item)
                elif isinstance(item, dict):
                    recursive_dict(item)

        def recursive_dict(D: dict):
            for key, value in D.items():
                if isinstance(value, str):
                    if value == '#' + key:
                        D[key] = kwargs.get(key, None)
                    else:
                        D[key] = value.format(**kwargs)
                elif isinstance(value, list):
                    recursive_list(value)
                elif isinstance(value, dict):
                    recursive_dict(value)

        recursive_dict(self.embed_info)
        recursive_dict(self.data)

        return self

    @property
    def embed(self) -> Embed:
        '''
        A `discord.Embed` object based off the `embed_info` attribute. Please use `set_embed` if you wish to reassign this to an Embed.
        '''
        return generate_embed(self.embed_info) if self._embed is None else self._embed

    @embed.setter
    def embed(self, _):
        raise AttributeError("Please use set_embed to change a state's embed")

    def add_action(self, *args):
        '''
        Appends the given action objects to the state's action list.
        The following two snippets are identical when a state has no actions; whichever used is up to personal preferance.
        ```python
        state.actions = [first_action, second_action, ...]
        state.add_action(first_action, second_action, ...)
        ```
        Raises a TypeError if any argument isn't an Action.
        '''
        for action in args:
            if not isinstance(action, Action): raise TypeError(f"Invalid object type: Expected 'Action', got {action.__class__.__name__}")
            self.actions.append(action)

        return self

    def remove_action(self, *args):
        '''
        Removes the first occurence of each given Action.\n
        Raises a TypeError if any given argument isn't an Action. Raises a ValueError if the given Action is not present.\n
        '''
        for action in args:
            if not isinstance(action, Action): raise TypeError(f"Invalid object type: Expected 'Action', got {action.__class__.__name__}")
            self.actions.remove(action)

        return self

    def remove_all_actions(self):
        '''
        Removes every action from the state by setting it to an empty list.
        '''
        self.actions = []
        return self

    def update_embed_info(self, new_embed: Embed):
        '''
        Updates `embed_info` based on the given Embed object. This will ignore any incompatible keys.\n
        Raises a TypeError if given something other than an Embed.
        '''
        if not isinstance(new_embed, Embed): raise TypeError(f"Invalid object type: Expected 'Embed' or 'NoneType', got {new_embed.__class__.__name__}")
        for key, value in new_embed.to_dict().items():
            if key in self.VALID_EMBED_KEYS:
                self.embed_info[key] = value

        return self

    def set_embed(self, new_embed: Embed | None):
        '''
        Reassigns the `embed` attribute of this state to the given Embed. The state will completely disregard `embed_info` and use this instead.
        Passing `None` to this method will disregard the previously set Embed and go back to using `embed_info`\n
        Raises a TypeError if given anything other than an Embed object or None.
        '''
        if not isinstance(new_embed, (Embed, NoneType)): raise TypeError(f"Invalid object type: Expected 'Embed' or 'NoneType', got {new_embed.__class__.__name__}")
        self._embed = new_embed
        return self

# ------------------------------------------------------------------------------------------------------------------------------------------------
#                                                              Beginning of Action
# ------------------------------------------------------------------------------------------------------------------------------------------------

async def _DefaultCallback(mach: Machine, interaction: Interaction):
    await mach.update_state(State(), interaction)

class Action(Button):
    '''
    An object representing a button within discord. Designed to work with the machine class.\n
    ## Parameters and Attributes\n
    All of the following parameters are keyword-only and optional. Unless otherwise specified, all parameters default to `None`. 
    Every parameter (except callback) is also an equivalently named attribute.
      `callback = DefaultCallback`: The coroutine that will be invoked when an Action object is interacted with. Defaults to changing to a generic state. \n
       Please see the callback section for further details on this parameter.\n
      `label`: The label (text) of the button.\n
      `emoji`: The emoji of the button. This may be a string or `discord.Emoji` object.\n
      `style = ButtonStyle.blurple`: The style for the button.\n
      `row`: The row the button should be placed in, must be between 0 and 4 (inclusive). If this isn't specified, then automatic ordering will be applied.\n
      `url`: A string representing the url that this button should send to. Note that specifying this changes some functionality (see discord.py docs).\n
      `disabled = False`: Whether the button should invoke `callback` whenever pressed.\n
    There is an additional attribute, `machine`, that refers to the machine that the button was most recently attached to. This is not a parameter and should not be modified.
    ## Methods\n
      `copy`: Returns a shallow copy of the button.
      `new`: A decorator that provides an alternate way to construct Action objects. See its docstring for more details.\n
    ## Callback\n
    Callback should be defined like so, where machine is the `Machine` this Action is attached to, and interaction is a `discord.Interaction` object.
    It is also recommended to use the `new` decorator if callback will be assigned to a single Action.
    ```python
    async def callback(machine, interaction)
        # Do stuff...
        await machine.update_state(...)
    ```
    A third parameter may be included, which corresponds to the Action object that invoked callback. 
    This may be useful for making a base action that uses metadata (label, style, etc) in its callback. Including this third parameter is completely optional and may be omitted.\n
    As the sample code suggests, it is expected that `callback` will generate a state object and call `update_state` onto its passed machine.
    '''
    def __init__(self, *, callback: Coroutine=_DefaultCallback , style: ButtonStyle=ButtonStyle.blurple, label: str | None=None, emoji: Emoji | None=None, row: int | None=None, url: str | None=None, disabled: bool=False):
        super().__init__(style=style, label=label, emoji=emoji, row=row, url=url, disabled=disabled)
        self.machine: Machine | None = None
        self.__callback = callback
        self.__two_args = len(signature(self.__callback).parameters) == 2

    async def callback(self, interaction):
        if self.__two_args:
            await self.__callback(self.machine, interaction)
        else:
            await self.__callback(self.machine, interaction, self)

    @classmethod
    def new(cls, **kwargs):
        '''
        A decorator used to be able to construct Action objects more easily. Sample use:
        ```python
        @Action.new(label='Click me!')
        async def do_something(machine, interaction):
            print('I was pressed!')
        ```
        This is equivalent to `do_something = Action(label='Click me!', callback=do_something)`. Note that the variable for the coroutine is reassigned to an Action object.
        ### Parameters
        All parameters are keyword-only, and unless otherwise specified, defaults to `None`.
          `label`: The label (text) of the button.\n
          `emoji`: The emoji of the button. This may be a string or `discord.Emoji` object.\n
          `style = ButtonStyle.blurple`: The style for the button.\n
          `row`: The row the button should be placed in, must be between 0 and 4 (inclusive). If this isn't specified, then automatic ordering will be applied.\n
          `url`: A string representing the url that this button should send to. Note that specifying this changes some functionality (see discord.py docs).\n
          `disabled = False`: Whether the button should invoke `callback` whenever pressed.
        '''
        def wrap(callback):
            return cls(callback=callback, **kwargs)

        return wrap

    def copy(self, *, callback: Coroutine | None=None , style: ButtonStyle | None=None, label: str | None=None, emoji: Emoji | None=None, row: int | None=None, url: str | None=None, disabled: bool=False):
        '''
        Returns a shallow copy of this Action.\n
        Specifying any parameters will set the copy's parameter to whatever is given. For example, specifying label cause this method to use the given string instead of the original action's label.
        '''
        return self.__class__( # This is used instead of Action() to allow support for inheritance
            callback=callback or self.__callback,
            style=style or self.style,
            label=label or self.label,
            emoji=emoji or self.emoji,
            row=row or self.row,
            url=url or self.url,
            disabled=disabled or self.disabled
        )

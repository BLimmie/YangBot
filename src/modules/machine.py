import discord
import discord_ui
from discord_ui import Listener
from discord.ext import commands
from discord_helper import generate_embed
from states import state
from action import action
from typing import List
from copy import deepcopy
import json
<<<<<<< HEAD
>>>>>>> 31d9088 (changed update_state)
=======
>>>>>>> a37d118 (Changed 'create' method to send a message, and updated 'update_state' a bit.)

'''
Our idea for implementation:

Machine: Represents the embed to be interacted with. Machine comes built in with a history, data, and a list of states (not necessary?)
Action: Represents some execution that happens when machine is interacted with (i.e. a button is pressed). Action is responsibile for determining next state, which can be updated via machine.update_state()
State: Represents the current state of the machine, i.e. a new embed and any related data. Actions manipulate (and create) states, which is passed onto a machine to update.

Key takeaways:

1. Actions are attached to buttons and its method is called whenever an interaction happens (button clicked). It is responsible for generating a new state which will be passed onto the machine.
2. Machine represents the embed itself. Its sole responsibility is to update itself, track a history, and hold data.
3. States are blueprints for what the machine should look like. It contains information about the embed and actions. (Should it contain new data too?)
'''

'''
In order to call certain actions via buttons, we can approach this one of two ways.

1. We can implement a general listener, similar to how messages are executed, and execute actions depending on the attributes. We will need to plan this and possibly recreate some stuff.
2. We can create custom IDs for buttons and attach listeners to those buttons. This will be easier to implement, however it will require us to develop a system of both creating IDs AND sharing them to all relevant objects.
'''

#This is mimics an interaction object in order to bypass all of the duck tests used below
class _interaction_mimic:
    def __init__(self, *, author = None) -> None:
        '''
        An object that mimics `discord_ui.ButtonInteraction` in order to bypass duck tests.

        Accepts the following parameters as keyword arguments, all of which are optional:
        `author`

        See `discord_ui.ButtonInteraction` for proper documentation of attributes.
        '''
        self.author = author

class machine:
    def __init__(self):
        '''
        Please use `machine.create()` to make a new machine, as this will return a blank object.
        '''
        pass
    
    @classmethod
    async def create(cls, client: commands.Bot, ui_client: discord_ui.UI, initial_state: state, message: discord.Message, * , channel: discord.TextChannel = None, history: List[action] = []):
        '''
        Initializes a machine that may only be modified by and interacted with its creator.
        
        ### Parameters
        `client`: The bot itself.
        `ui_client`: A UI extension allowing parsing of interactions. Must be initialized via `UI(client)` (should every machine initialize its own, or is it better to have one made then passed to all?)
        `initial_state`: A state object that the machine should put itself into upon creation.
        `message`: The message that initialized the machine.
        `channel` (Optional): The channel that the machine should initialize in. Defaults to `message.channel`.
        `history` (Optional): A history of previous actions taken. Empty by default.
        '''

        # Initialize 'private' variables
        self = cls()
        self._client = client
        self._ui = ui_client
        self._owner = message.author
        self._message = await ui_client.components.send(channel or message.channel, content = 'Initializing...')

        # Initialize 'public' variables
        self.history = deepcopy(history)

        # Put the machine into its initial state
        self.current_state = None
        await self.update_state(initial_state, _interaction_mimic(owner=self._owner))

<<<<<<< HEAD
    async def update_state(self, user_action: action, interaction: Interaction):
>>>>>>> 31d9088 (changed update_state)
=======
        return self

<<<<<<< HEAD
    async def update_state(self, new_state: state, interaction: discord_ui.ButtonInteraction):
>>>>>>> a37d118 (Changed 'create' method to send a message, and updated 'update_state' a bit.)
        """
=======
    async def update_state(self, new_state: state, interaction: discord_ui.ButtonInteraction) -> None:
        '''
>>>>>>> 38d6301 (Further changed machines.py, left comments within script explaining vision)
        Edits the machine to match the given state.

        ### Parameters
        `new_state`: The state the machine should update itself to be in.
        `interaction`: The interaction object that prompted a change in state.
        '''
        if not self.interaction_check(interaction.author): return

        self.current_state = new_state
        self._message.edit(
            content = '',
            embed=generate_embed(json.loads(new_state.template)), 
            components=[self.current_state.json.loads(self.new_state.template)["buttons"]]
        )
    
<<<<<<< HEAD
    client=discord.ext.commands.Bot()    
    @client.listen()
    async def interaction_check(self, interaction: Interaction, message) -> bool:
        await message.user == message.author
>>>>>>> 31d9088 (changed update_state)
=======
    def interaction_check(self, user: discord.User) -> bool:
<<<<<<< HEAD
        return user.id == self._owner.id
>>>>>>> a37d118 (Changed 'create' method to send a message, and updated 'update_state' a bit.)
=======
        '''
        Determines if an interactive is valid. Returns `True` if so, otherwise returns `False`.
>>>>>>> 38d6301 (Further changed machines.py, left comments within script explaining vision)

        ### Parameters
        `user`: A `discord.User` object. `discord.Member` is acceptable too as it subclasses `discord.User`.
        '''
        return user.id == self._owner.id
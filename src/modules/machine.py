import discord
import discord_ui
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
Our idea for Machine:

Machine serves as a gateway to the embed (i.e. it is the machine itself). Machine's responsibility is holding data and updating its own state. It receives states from Action objects.
'''

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

#This is mimics an interaction object in order to bypass all of the duck tests used below
class interaction_mimic:
    def __init__(self, owner = None) -> None:
        '''
        An object that mimics `discord_ui.ButtonInteraction` in order to bypass duck tests.

        Accepts the following parameters, all of which are optional:
        `owner`

        See `discord_ui.ButtonInteraction` for proper documentation of attributes.
        '''
        self.author = owner

class machine:
    def __init__(self):
        '''
        Please use `machine.create()` to make a new machine, as this will return a blank object.
        '''
        pass
    
    @classmethod
    async def create(cls, client: commands.Bot, ui_client: discord_ui.UI, message: discord.Message, initial_state: state, * , states: List[state] = [], actions: List[action] = [], history: List[action] = []):
        '''
        Initializes a machine that may only be modified by interacted with by its creator.
        
        @params
        `client`: The bot itself.
        `ui_client`: A UI extension allowing parsing of interactions. Must be initialized as UI(client) (should every machine initialize its own, or is it better to have one made then passed to all?)
        `message`: The message that initialized the machine.
        `initial_state`: A state object that the machine should put itself into upon creation.
        `states` (Optional?): A list of states the machine may enter. Empty by default.
        `actions` (Optional?): A list of valid actions the user may perform. Empty by default.
        `history` (Optional): A history of previous actions taken. Empty by default.
        '''

        # Initialize 'private' variables
        self = cls()
        self._client = client
        self._ui = ui_client
        self._owner = message.author
        self._message = await ui_client.send(message.channel, content = 'Initializing...')

        # Initialize 'public' variables
        self.states = deepcopy(states)
        self.actions = deepcopy(actions)
        self.history = deepcopy(history)

        # Put the machine into its initial state
        self.current_state = None
        await self.update_state(initial_state, interaction_mimic(self._owner))

<<<<<<< HEAD
    async def update_state(self, user_action: action, interaction: Interaction):
>>>>>>> 31d9088 (changed update_state)
=======
        return self

    async def update_state(self, new_state: state, interaction: discord_ui.ButtonInteraction):
>>>>>>> a37d118 (Changed 'create' method to send a message, and updated 'update_state' a bit.)
        """
        Edits the machine to match the given state.

        @params
        `new_state`: The state the machine should update itself to be in.
        `interaction`: The interaction object that prompted a change in state.
        """
        if not self.interaction_check(interaction.author): return

        # maybe use interaction_check
        self.current_state = new_state
        self._message.edit(
            content = '',
            embed=generate_embed(json.loads(self.new_state.template)), 
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
        return user.id == self._owner.id
>>>>>>> a37d118 (Changed 'create' method to send a message, and updated 'update_state' a bit.)

    def add_state(self, newState: state):
        if newState not in self.states:
            self.states.append(newState)

    def add_action(self, newAction: action):
        if newAction not in self.actions:
            self.actions.append(newAction)

    def set_initial_state(self, initial_state: state):
        self.current_state = initial_state
import discord
from discord.ext import commands
import discord_ui
from states import state
from action import action
from typing import List
from copy import deepcopy
<<<<<<< HEAD
from discord_helper import generate_embed
=======
import discord.ext.commands
from discord_ui import Button, Interaction
from src.modules.discord_helper import generate_embed
import json
>>>>>>> 31d9088e19512adf823669ddd01534c5fc187adb

'''
Our idea for Machine:

Machine serves as a gateway to the embed (i.e. it is the machine itself). Machine's responsibility is holding data and updating its own state. It receives states from Action objects.
'''

'''
Our idea for implementation:

Machine: Represents the embed to be interacted with. Machine comes built in with a history, data, and a list of states (not necessary?)
Action: Represents some execution that happens when machine is interacted with (i.e. a button is pressed). Action is responsibile for determining next state, which can be updated via machine.update_state
State: Represents the current state of the machine, i.e. a new embed and any related data. Actions manipulate (and create) states, which is passed onto a machine to update.

Key takeaways:

1. Actions are attached to buttons and its method is called whenever an interaction happens (button clicked). It is responsible for generating a new state which will be passed onto the machine.
2. Machine represents the embed itself. Its sole responsibility is to update itself, track a history, and hold data.
3. States are blueprints for what the machine should look like. It contains information about the embed and actions. (Should it contain new data too?)
'''

class machine:
    def __init__(self):
        '''
        Please use machine.create() to make a new machine, as this will return a blank object.
        '''
        pass
    
    @classmethod
    async def create(cls, client: commands.Bot, message: discord.Message = None, initial_state: state = None, * , states: List[state] = [], actions: List[action] = [], history: List[action] = []):
        '''
        Initializes a machine that may only be modified by interacted with by its creator.
        
        @params
        `client`: The bot itself.
        `message`: The message that initialized the machine.
        `initial_state`: A state object that the machine should put itself into upon creation.
        `states`: A list of states the machine may enter (?). Empty by default.
        `actions`: A list of valid actions the user may perform (?). Empty by default.
        `history`: A history of previous actions taken. Empty by default.
        '''
        self = machine()
        self._owner = message.author
        self._channel = message.channel
        self.states = deepcopy(states)
        self.actions = deepcopy(actions)
        self.history = deepcopy(history)
<<<<<<< HEAD
        self.current_state = initial_state
        await self.update_state(initial_state)
        return self
        
    async def update_state(self, user_action: state = None):
=======
        self.current_state = current_state
        self.update_state(current_state)

    async def update_state(self, user_action: action, interaction: Interaction):
>>>>>>> 31d9088e19512adf823669ddd01534c5fc187adb
        """
         1. Call determine_next_state and update self.current_state
         2. Edit embed with new attributes
         3. update history
        """
        # maybe use interaction_check

        self.current_state = user_action.determine_next_state()
        self.history.append(user_action)

<<<<<<< HEAD
    def interaction_check(self, user: discord.User) -> bool:
        '''
        Checks if an interaction is valid, i.e. if the provided user is the same as the creator of the state machine.
        '''
        return user.id == self._owner.id
=======
        interaction.edit(embed=generate_embed(json.loads(self.current_state.template)), 
        components=[self.current_state.json.loads(self.current_state.template)["buttons"]])
    
    client=discord.ext.commands.Bot()    
    @client.listen()
    async def interaction_check(self, interaction: Interaction, message) -> bool:
        await message.user == message.author
>>>>>>> 31d9088e19512adf823669ddd01534c5fc187adb

    def add_state(self, newState: state):
        if newState not in self.states:
            self.states.append(newState)

    def add_action(self, newAction: action):
        if newAction not in self.actions:
            self.actions.append(newAction)

    def set_initial_state(self, initial_state: state):
        self.current_state = initial_state

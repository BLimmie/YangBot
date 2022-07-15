import discord
from states import state
from actions import action
from typing import List
from copy import deepcopy
from src.tools.message_return import message_data
from discord_ui import Button, Interaction
from src.modules.discord_helper import generate_embed

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
    def __init__(self, channel: discord.TextChannel, current_state: state, * , states: List[state] = [], actions: List[action] = [], history: List[action] = []):
        self.channel = channel
        self.states = deepcopy(states)
        self.actions = deepcopy(actions)
        self.history = deepcopy(history)
        self.current_state = current_state
        self.update_state(current_state)
        
    async def update_state(self, user_action: state):
        """
         1. Call determine_next_state and update self.current_state
         2. Edit embed with new attributes
         3. update history
        """
        # Do stuff to change the current state
        self.history.append(user_action)

    async def interaction_check(self, interaction: Interaction, message) -> bool:
        await message.user == message.author

    def add_state(self, newState: state):
        if newState not in self.states:
            self.states.append(newState)

    def add_action(self, newAction: action):
        if newAction not in self.actions:
            self.actions.append(newAction)

    def set_initial_state(self, initial_state: state):
        self.current_state = initial_state
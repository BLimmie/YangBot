import discord
from states import state
from action import action
from typing import List
from copy import deepcopy
from src.tools.message_return import message_data
<<<<<<< HEAD
import discord.ext.commands
from discord_ui import Button, Interaction
from src.modules.discord_helper import generate_embed
import json

class machine:
    def __init__(self, channel: discord.TextChannel, *, states: List[state], actions: List[action], history, current_state: state):
=======
from discord_ui import Button, Interaction
from src.modules.discord_helper import generate_embed

class machine():
    def __init__(self, states: List[state], actions: List[action], history, current_state: state):
>>>>>>> 18943fc (first draft)
        """
        @param states: list of all possible states
        @param history: list of user's selected actions
        """
        self.states = deepcopy(states)
        self.actions = deepcopy(actions)
        if history == None:
            history = []
        else:
            self.history = deepcopy(history)
        self.current_state = current_state
        
<<<<<<< HEAD
        if states[0] != None:
            channel.send(states[0])

    async def update_state(self, user_action: action, interaction: Interaction):
=======

    async def update_state(self, user_action: action):
>>>>>>> 18943fc (first draft)
        """
         1. Call determine_next_state and update self.current_state
         2. Edit embed with new attributes
         3. update history
        """
<<<<<<< HEAD
        # maybe use interaction_check

        self.current_state = user_action.determine_next_state()
        self.history.append(user_action)

        interaction.edit(embed=generate_embed(json.loads(self.current_state.template)), 
        components=[self.current_state.json.loads(self.current_state.template)["buttons"]])
    
    client=discord.ext.commands.Bot()    
    @client.listen()
=======
        self.current_state = user_action.determine_next_state()
        self.history.append(user_action)

        self.embed_dict = action.state_choice.embed.to_dict()
        
        for attribute in self.embed_dict:
            if 'fields' in self.embed_dict:
                for item in self.embed['fields']:
                    self.embed.add_field(name=item['name'],value=item['value'],inline=item['inline'] if 'inline' in item else False)
            
            elif attribute in vars(self.embed).keys():
                self.embed.attribute = self.embed_dict[attribute]
        self.embed = discord.Embed.from_dict(self.embed_dict)
        await discord.message.edit(embed=self.embed)

>>>>>>> 18943fc (first draft)
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

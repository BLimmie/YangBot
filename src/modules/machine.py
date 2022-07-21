from multiprocessing import dummy
import discord
import discord_ui
from discord.ext import commands
from discord_helper import generate_embed
from states import state
from action import action
from typing import List
from copy import deepcopy
import json


#This is mimics an interaction object in order to bypass all of the duck tests used below
class _InteractionMimic:
    '''
    An object that mimics `discord_ui.ButtonInteraction` in order to bypass duck tests.

    Accepts the following parameters as keyword arguments, all of which are optional:
    `author`

    See `discord_ui.ButtonInteraction` for proper documentation of attributes.
    '''
    def __init__(self, *, author = None) -> None:
        self.author = author

class _IndividualListener(Listener):
    '''
    A Listener subclass that allows interaction with single buttons. Maybe this should be the action class??
    
    The alternative is to develop a general method (similar to `message_on_command`) that takes in context from all button clicks would need to developed.
    '''

    def __init__(self, id: str, callback, timeout=None, target_users=None) -> None:
        '''
        Initializes a Listener tied to a given button.

        ### Parameters
        `id`: The ID of a button to listen to.
        `callback`: The coroutine to be executed when the button is pressed. Will be passed a `ButtonInteraction` object.
        '''
        super().__init__(timeout, target_users)

        @Listener.button(id) # Is this valid?? Does the decorator need to be called within the class? Or is it fine to do it here?
        async def execute(self, ctx):
            await callback(ctx)

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
        
        ## Parameters
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
        await self.update_state(initial_state, _InteractionMimic(author=self._owner))
        return self

    async def update_state(self, new_state: state, interaction: discord_ui.ButtonInteraction) -> None:
        '''
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
        )
    
    def interaction_check(self, user: discord.User) -> bool:
        '''
        Determines if an interactive is valid. Returns `True` if so, otherwise returns `False`.
        '''
        return user.id == self._owner.id
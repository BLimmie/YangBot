from typing import List
from copy import deepcopy
from discord import Embed, ButtonStyle
from discord.ui import Button
from discord_helper import generate_embed

class state:
    '''
    An object representing a state for a machine. Behaves like a dictionary (see Behavior)

    ### Attributes

    `embed_info`: A dictionary describing attributes for a discord.Embed object

    `data`: Any other data relevant for the machine.

    `embed`: A `discord.Embed` object created with `embed_info`.
    
    ### Behavior

    This class behaves like a dictionary.

    For getting values, it will return `embed_info[key]`. If it doesn't exist, then `data[key]` will be returned instead. 
    
    For setting values, it will check if the key is present in `embed_info`. If it is, then `embed_info[key] = value`. Otherwise, `data[key] = value`.
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
        return self.embed_info[key] if key in self.embed_info else self.data[key]

    def __setitem__(self, key, value) -> None:
        if key in self.embed_info:
            self.embed_info[key] = value
        else:
            self.data[key] = value

    @classmethod
    def from_dict(cls, embed_dict: dict,*, buttons: List[Button] = [], data: dict = {}):
        '''
        Creates a state based on the given dictionaries. Performs a shallow copy on all passed parameters.

        ## Parameters

        `embed_dict`: A dictionary with a list of attributes. All keys are optional; any missing keys will be given default values. See attributes of `discord.Embed` for a list of valid key-value pairs.
        `buttons` (Optional): A list of Button objects. Empty by default.
        `data` (Optional): A dictionary with all relevant data for the machine. Empty by default.
        '''
        self = cls()
        for key, value in embed_dict.items():
            if key in self.embed_info:
                self.embed_info[key] = value
            else:
                print('Unknown key "' + str(key) + '" with value "' + str(value) + '" given while attempting to generate a state.')
        
        self.data = data.copy()
        self.buttons = buttons.copy()
        return self

    @classmethod
    def from_state(cls, other_state):
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
        self.buttons = [Button(style=button.style or ButtonStyle.blurple, label=button.label, url=button.url, emoji=button.emoji, row=button.row) for button in other_state.buttons]
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
        
if __name__ == "__main__":
    # To test: How to add buttons to message. Seems like it's as simple as modifying `message.components`.
    embed = generate_embed({
            "title": "hey",
            "description": "yo",
            "color": 16777215
        })
    new_state = state()
    new_state.embed = 'test'
    print(new_state.embed_info)

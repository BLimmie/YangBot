from typing import List
from copy import deepcopy
from discord import Embed, ButtonStyle
from discord.ui import Button
from discord_helper import generate_embed

class state:
    '''
    An object representing a state for a machine. Behaves like a dictionary for its data, like an object for its embed (see Behavior).

    ## Attributes

    `embed_info`: A dictionary describing attributes for a `discord.Embed` object

    `embed`: A `discord.Embed` object created with `embed_info`.

    `buttons`: A list of `discord.ui.Button` objects.

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
    def from_dict(cls, embed_dict: dict, *, buttons: List[Button] = [], data: dict = {}):
        '''
        Creates a state based on the given dictionaries. Performs a shallow copy on all passed parameters.

        ## Parameters

        `embed_dict`: A dictionary with a list of attributes. All keys are optional; any missing keys will be given default values. See attributes of `discord.Embed` for a list of valid key-value pairs.

        `buttons` (Optional): A list of Button objects. Empty by default.

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
    new_state = state.from_dict({
        "title": "hey",
        "color": 5
    }, data={'first': 1})
    new_state.buttons = ['yo']
    print(new_state.buttons)
    print(new_state['first'])


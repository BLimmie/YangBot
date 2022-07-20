<<<<<<< HEAD
import json
<<<<<<< HEAD
from discord_ui import Button
from discord_helper import generate_embed

=======
import discord.ext.commands
from src.modules.discord_helper import generate_embed
>>>>>>> a37d118 (Changed 'create' method to send a message, and updated 'update_state' a bit.)
=======
import discord.ext.commands
from src.modules.discord_helper import generate_embed
from discord import Embed

>>>>>>> 6b84dbc (Added some additional methods to state, and changed its structure. Removed any use of JSON objects, since we'll be using buttons)
'''
Idea for State:

State is a blueprint which can be read by Machine to update itself. It does not do much on its own. Action is responsible for generating new states to pass onto machine, while machine is responsible for updating itself depending on the action.
'''

class state:
    def __init__(self):
        '''
        Initializes a blank state i.e. all fields are present but are empty. Default color is white.
        '''
        self.embed_info = {
            "title": "",
            "subtitle": "",
            "color": 16777215,
            "fields": [],
            "components": []
        }
        self.data = {}

<<<<<<< HEAD
<<<<<<< HEAD
    def fill_template(self, **kwargs):
        filled_temp = json.loads(self.template).format(kwargs)
        # instead here use generate_embed
        return json.dumps(filled_temp)
=======
    def fill_template(self, embed_dict):
        embed = generate_embed(embed_dict)
        filled_temp = json.loads(self.template).format(embed.__dict__)
        return json.dumps(filled_temp)
=======
    @classmethod
    def from_dic(cls, embed_dict: dict, data: dict = {}):
        '''
        Creates a state based on the given dictionaries. Performs a shallow copy on both `embed_dict` and `data`.

        ### Parameters
        `embed_dict`: A dictionary with a list of attributes. Every key pair is optional; any missing keys pairs will be given default values. See `discord.Embed`'s attributes for a list of valid keys.
        `data` (Optional): A dictionary with all relevant data for the machine. Defaults to a blank dictionary (`{}`)
        '''
        self = cls()
        for key, value in embed_dict.items():
            if key in self.embed_info:
                self.embed_info[key] = value
            else:
                print('Unknown key "' + str(key) + '" with value "' + str(value) + '" given while attempting to generate a state.')
        
        for key, value in data.items():
            self.data[key] = value

        return self

    @property
    def embed(self) -> Embed:
        '''
        Returns a `discord.Embed` object based off the state's `embed_info` attribute.
        '''
        return generate_embed(self.embed_info)
>>>>>>> 6b84dbc (Added some additional methods to state, and changed its structure. Removed any use of JSON objects, since we'll be using buttons)

>>>>>>> a37d118 (Changed 'create' method to send a message, and updated 'update_state' a bit.)

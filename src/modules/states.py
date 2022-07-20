import json
<<<<<<< HEAD
from discord_ui import Button
from discord_helper import generate_embed

'''
Idea for State:

State is a blueprint which can be read by Machine to update itself. It does not do much on its own. Action is responsible for generating new states to pass onto machine, while machine is responsible for updating itself depending on the action.
'''

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
=======
    def __getitem__(self, key):
        return self.embed_info[key] if key in self.embed_info else self.data[key]

    def __setitem__(self, key: str, value) -> None:
        if key in self.embed_info:
            self.embed_info[key] = value
        else:
            self.data[key] = value

>>>>>>> c9f1377 (Finalized 'state' object)
    @classmethod
    def from_dict(cls, embed_dict: dict, data: dict = {}):
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
    def embed(self):
        '''
        A `discord.Embed` object based off the `embed_info` attribute.
        '''
<<<<<<< HEAD
        return generate_embed(self.embed_info)
>>>>>>> 6b84dbc (Added some additional methods to state, and changed its structure. Removed any use of JSON objects, since we'll be using buttons)

>>>>>>> a37d118 (Changed 'create' method to send a message, and updated 'update_state' a bit.)
=======
        return generate_embed(self.embed_info)
>>>>>>> c9f1377 (Finalized 'state' object)

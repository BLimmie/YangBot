import json
<<<<<<< HEAD
from discord_ui import Button
from discord_helper import generate_embed

=======
import discord.ext.commands
from src.modules.discord_helper import generate_embed
>>>>>>> a37d118 (Changed 'create' method to send a message, and updated 'update_state' a bit.)
'''
Idea for State:

State is a blueprint which can be read by Machine to update itself. It does not do much on its own. Action is responsible for generating new states to pass onto machine, while machine is responsible for updating itself depending on the action.
'''
class state:
    def __init__(self):
        dictionary = {
            "title": "{title}",
            "subtitle": "{subtitle}",
             "fields": [
                {"name": "name1", "value": "value1"},
                {"name": "name2", "value": "value2"},],
            "buttons": []
        }
        self.template = json.dumps(dictionary)

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

>>>>>>> a37d118 (Changed 'create' method to send a message, and updated 'update_state' a bit.)

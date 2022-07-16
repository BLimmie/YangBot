import json
from discord_ui import Button
from discord_helper import generate_embed

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

    def fill_template(self, **kwargs):
        filled_temp = json.loads(self.template).format(kwargs)
        # instead here use generate_embed
        return json.dumps(filled_temp)

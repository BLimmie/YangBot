import discord
import json
import discord.ext.commands
from discord_ui import Button
from src.modules.discord_helper import generate_embed

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

    def fill_template(self, embed_dict):
        embed = generate_embed(embed_dict)
        filled_temp = json.loads(self.template).format(embed.__dict__)
        return json.dumps(filled_temp)



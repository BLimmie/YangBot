import discord
import json
<<<<<<< HEAD
import discord.ext.commands
from discord_ui import Button
from src.modules.discord_helper import generate_embed

class state:
=======
from src.tools.message_return import message_data
from discord_ui import Button
from src.modules.discord_helper import generate_embed

class state():
>>>>>>> 18943fc (first draft)
    def __init__(self):
        dictionary = {
            "title": "{title}",
            "subtitle": "{subtitle}",
<<<<<<< HEAD
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

=======
            "button1" : Button(label="label1"),
            "button2" : Button(label2="label1"),
             "fields": [
                {"name": "name1", "value": "value1"},
                {"name": "name2", "value": "value2"},]
        }
        self.template = json.dumps(dictionary)

    def fill_template(self, **kwargs):
        filled_temp = json.loads(self.template).format(kwargs)
        # instead here use generate_embed
        return json.dumps(filled_temp)

    def generate_embed(self, message, **kwargs):
        return message_data(message.channel, discord.Embed(kwargs))
>>>>>>> 18943fc (first draft)


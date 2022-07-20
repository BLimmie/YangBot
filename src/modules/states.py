from discord import Embed
from src.modules.discord_helper import generate_embed
from copy import deepcopy

"""
Idea for State:

State is a blueprint which can be read by Machine to update itself. It does not do much on its own. Action is responsible for generating new states to pass onto machine, while machine is responsible for updating itself depending on the action.
"""
class state:
    def __init__(self):
        self.embed_info = {
            "title": "{title}",
            "subtitle": "{subtitle}",
             "fields": [],
            "buttons": []
        }
        self.data = {}

    @property
    def embed(self) -> Embed:
        """
        Returns discord.Embed object based off the state's embed_info function
        """
        return generate_embed(self.embed_info)

    @classmethod
    def from_dic(self, embed_dict: dict, data: dict = {}):
        self.embed_info = deepcopy(self.embed().__dict__)
        self.data = deepcopy(data)



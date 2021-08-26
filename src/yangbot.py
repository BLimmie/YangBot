import traceback
from typing import List

import discord

from src.commands import command_on_message
from src.auto_on_message import auto_on_message
from src.member_join import on_member_join
from src.member_update import on_member_update


class YangBot():
    def __init__(self, dbconn, client, config, repeated_messages=4):
        """
        Initialization of all data
        """
        # Debug
        self.debug = False

        # All necessary data
        self.client = client
        self.conn = dbconn
        self.config = config

        # Functions
        self.command_on_message_list = {}
        self.auto_on_message_list = {}
        self.on_member_join_list = {}
        self.on_member_update_list = {}

        self.channels = list(self.client.get_all_channels())
        self.repeat_n = repeated_messages
        self.repeated_messages_dict = {(channel.id):[] for channel in self.channels}

        # All Server Role IDs
        guild = client.get_guild(config["server_id"]) # UCSB Server ID
        roles = {}
        for r in guild.roles:
            roles.update({r.name: r.id})
        self.roles = roles

        # Actions in Command on Message
        for action in command_on_message.__subclasses__():
            self.command_on_message_list[action.__name__] = action(bot = self)
    
        # Actions in Auto on Message
        for action in auto_on_message.__subclasses__():
            self.auto_on_message_list[action.__name__] = action(bot = self)

        # Actions on Member Join
        for action in on_member_join.__subclasses__():
            self.on_member_join_list[action.__name__] = action(bot = self)
    
        # Actions on Member Update
        for action in on_member_update.__subclasses__():
            self.on_member_update_list[action.__name__] = action(bot = self)

    # Run Command on Message
    async def run_command_on_message(self, message):
        if message is not None:
            command = message.content.split()[0][1:]
            if command in self.command_on_message_list:
                print(command)
                return await self.command_on_message_list[command].proc(message, message.created_at, message.author)
            
    # Run Auto on Message            
    async def run_auto_on_message(self, message): 
        if message is not None:
            for key, func in self.auto_on_message_list.items():
                try:
                    function = await func.proc(message, message.created_at, message.author)
                    if function is not None:
                        return function
                except Exception:
                    traceback.print_exc()
                    assert False
    
    # Run on Member Join
    async def run_on_member_join(self, user):
        for func in self.on_member_join_list.values():
            return await func.simple_proc(user)
    
    # Run on Member Update
    async def run_on_member_update(self, before, after):
        for func in self.on_member_update_list.values():
            return await func.simple_proc(before, after)

    def get_roles(self, role_ids: List[str]) -> List[int]:
        return [self.roles[id] for id in role_ids]
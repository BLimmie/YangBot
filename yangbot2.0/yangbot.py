import discord
import asyncio

from tools.funcblocker import funcblocker
from tools.message_return import message_data


class YangBot():
    def __init__(self, dbcur, client):
        """
        Initialization of all data and functions of the bot
        """
        # Functions
        self.auto_on_message = {}
        self.command_on_message = {}
        self.react_option = {}
        self.on_user_change = {}

        # All necessary data
        self.cur = dbcur
        self.client = client

    async def send_message(message_info):
        """
        Sends message to channel in message_info
        """
        if message_info is None:
            return
        if message_info.content is None:
            return
        if isinstance(message_info.channel, int):
            channel = self.client.get_channel(message_info.channel)
        else:
            channel = message_info.channel
        channel.send(message_info.content)

    def auto_on_message(timer = None, roles = None, positive_roles = True):
        """
        Decorator for automatic on_message function
        
        args:
        timer (timedelta) = time between procs
        roles (list of string) = role names to check
        positive_roles (boolean) = True if only proc if user has roles, False if only proc if user has none of the roles
        secondary_args:
        func (function) = function to run, returns a message_data
        """
        def wrap(func):
            def wrapper(message):
                message_info = func(message)
            
            self.auto_on_message[func.__name__] = funcblocker(wrapper, timer, roles, positive_roles)
            return wrapper
        return wrap

    async def run_auto_on_message(message):
        for key, func in self.auto_on_message:
            message_info = func.proc(message.created_at, message.author, message)
            await send_message(message_info)

    def command_on_message(timer = None, roles = None, positive_roles = True):
        """
        Decorator for command on_message function
        name of the function is the command YangBot looks for
        
        e.g. 
        
        def test(message):
            return message_data(0000000000, message.content)
        
        procs on $test

        args:
        timer (timedelta) = time between procs
        roles (list of string) = role names to check
        positive_roles (boolean) = True if only proc if user has roles, False if only proc if user has none of the roles
        secondary_args:
        func (function) = function to run, returns a message_data
        """
        def wrap(func):
            def wrapper(message):
                message_info = func(message)

            self.auto_on_message[func.__name__] = funcblocker(wrapper, timer, roles, positive_roles)
            return wrapper
        return wrap
    
    async def run_command_on_message(message):
        """
        Precondition: message content starts with '$'
        """
        command = message.content.split()[0][1:]
        if command in self.command_on_message:
            message_info = self.command_on_message[command].proc(message.created_at, message.author, message)
            await send_message(message_info)

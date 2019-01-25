import discord
import asyncio
import inspect

from src.tools.funcblocker import funcblocker
from src.tools.message_return import message_data


class YangBot():
    def __init__(self, dbconn, client):
        """
        Initialization of all data and functions of the bot
        """
        # Functions
        self.auto_on_message_list = {}
        self.command_on_message_list = {}
        self.react_option = {}
        self.on_user_change = {}
        self.on_member_join_list = {}

        # All necessary data
        self.conn = dbconn
        self.client = client

    async def send_message(self, message_info):
        """
        Sends message to channel in message_info
        """
        if message_info is None:
            return
        if message_info.message is None:
            return
        if isinstance(message_info.channel, int):
            channel = self.client.get_channel(message_info.channel)
        else:
            channel = message_info.channel
        await channel.send(message_info.message)

    def auto_on_message(self, timer = None, roles = None, positive_roles = True, coro = None):
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
                return func(message)
            
            self.auto_on_message_list[func.__name__] = funcblocker(wrapper, timer, roles, positive_roles, coro)
            return wrapper
        return wrap

    async def run_auto_on_message(self, message, *args):
        for func in self.auto_on_message_list.values():
            message_info = func.proc(message.created_at, message.author, message)
            await self.send_message(message_info)
            if func.coro is not None:
                await func.coro(*args)

    def command_on_message(self, timer = None, roles = None, positive_roles = True, coro = None):
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
                return func(message)

            self.command_on_message_list[func.__name__] = funcblocker(wrapper, timer, roles, positive_roles, coro)
            return wrapper
        return wrap
    
    async def run_command_on_message(self, message, *args):
        """
        Precondition: message content starts with '$'
        """
        command = message.content.split()[0][1:]
        if command in self.command_on_message_list:
            message_info = self.command_on_message_list[command].proc(message.created_at, message.author, message)
            await self.send_message(message_info)
            if self.command_on_message_list[command].coro is not None:
                await self.command_on_message_list.coro(*message_info.args)

    def on_member_join(self, timer = None, roles = None, positive_roles = True, coro = None):
        def wrap(func):
            def wrapper(user):
                return func(user)
            self.on_member_join_list[func.__name__] = funcblocker(wrapper, timer, roles, positive_roles, coro)
            return wrapper
        return wrap
    
    async def run_on_member_join(self, user, *args):
        for func in self.on_member_join_list.values():
            if inspect.iscoroutinefunction(func.func):
                message_info = await func.simple_proc(user)
            else:
                message_info = func.simple_proc(user)
            await self.send_message(message_info)
            if func.coro is not None:
                await func.coro(*message_info.args)
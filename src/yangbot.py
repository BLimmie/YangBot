from src.tools.funcblocker import funcblocker


class YangBot():
    def __init__(self, dbconn, client, config, repeated_messages=4):
        """
        Initialization of all data and functions of the bot
        """
        # Functions
        self.auto_on_message_list = {}
        self.command_on_message_list = {}
        self.react_option = {}
        self.on_user_change = {}
        self.on_member_join_list = {}
        self.on_member_update_list = {}

        # All necessary data
        self.conn = dbconn
        self.client = client
        self.config = config

        self.channels = list(self.client.get_all_channels())
        self.repeat_n = repeated_messages
        self.repeated_messages_dict = {(channel.id):[] for channel in self.channels}

    async def send_message(self, message_info):
        """
        Sends message to channel in message_info
        """
        if message_info is None:
            return
        if message_info.message is None and message_info.embed is None:
            return
        if isinstance(message_info.channel, int):
            channel = self.client.get_channel(message_info.channel)
        else:
            channel = message_info.channel
        message = await channel.send(message_info.message, embed=message_info.embed)
        return message

    def auto_on_message(self, timer=None, roles=None, positive_roles=True, coro=None):
        """
        Decorator for automatic on_message function

        e.g.

        @bot.auto_on_message(timer, roles, positive_roles, coro)
        def test(message):
            return message_data(0000000000, message.content, args, kwargs)

        procs on every message

        args:
        timer (timedelta) = time between procs
        roles (list of string) = role names to check
        positive_roles (boolean) = True if only proc if user has roles, False if only proc if user has none of the roles
        coro (coroutine) = coroutine to run after function finishes running
        secondary_args:
        func (function) = function to run, returns a message_data
        """
        def wrap(func):
            def wrapper(message):
                return func(message)
            self.auto_on_message_list[func.__name__] = funcblocker(
                wrapper, timer, roles, positive_roles, coro)
            return wrapper
        return wrap

    async def run_auto_on_message(self, message):
        print(self.auto_on_message_list["fire"].last_time)
        if message is not None:
            for func in self.auto_on_message_list.values():
                message_info = func.proc(
                    message.created_at, message.author, message)
                send_message = await self.send_message(message_info)
                if func.coro is not None and message_info is not None:
                    await func.coro(send_message, *message_info.args, **message_info.kwargs)

    def command_on_message(self, timer=None, roles=None, positive_roles=True, coro=None):
        """
        Decorator for command_on_message function
        name of the function is the command YangBot looks for

        e.g.

        @bot.command_on_message(timer, roles, positive_roles, coro)
        def test(message):
            return message_data(0000000000, message.content, args, kwargs)

        procs on $test

        args:
        timer (timedelta) = time between procs
        roles (list of string) = role names to check
        positive_roles (boolean) = True if only proc if user has roles, False if only proc if user has none of the roles
        coro (coroutine) = coroutine to run after function finishes running
        secondary_args:
        func (function) = function to run, returns a message_data
        """
        def wrap(func):
            def wrapper(message):
                return func(message)
            self.command_on_message_list[func.__name__] = funcblocker(
                wrapper, timer, roles, positive_roles, coro)
            return wrapper
        return wrap

    async def run_command_on_message(self, message):
        """
        Precondition: message content starts with '$'
        """
        command = message.content.split()[0][1:]
        if command in self.command_on_message_list:
            message_info = self.command_on_message_list[command].proc(
                message.created_at, message.author, message)
            send_message = await self.send_message(message_info)
            if self.command_on_message_list[command].coro is not None and message_info is not None:
                await self.command_on_message_list[command].coro(send_message, *message_info.args, **message_info.kwargs)

    def on_member_join(self, coro=None):
        """
        Decorator for on_member_join function

        e.g.

        @bot.on_member_join(coro)
        def test(user):
            return message_data(None, None, args, kwargs)

        procs on all member joins

        args:
        coro (coroutine) = coroutine to run after function finishes running
        secondary_args:
        func (function) = function to run, returns a message_data
        """
        def wrap(func):
            def wrapper(user):
                return func(user)
            self.on_member_join_list[func.__name__] = funcblocker(
                wrapper, coro=coro)
            return wrapper
        return wrap

    async def run_on_member_join(self, user):
        for func in self.on_member_join_list.values():
            message_info = func.simple_proc(user)
            message = await self.send_message(message_info)
            if func.coro is not None and message_info is not None:
                await func.coro(message, *message_info.args, **message_info.kwargs)

    def on_member_update(self, coro=None):
        """
        Decorator for on_member_udpate function

        e.g.

        @bot.on_member_update(coro)
        def test(user):
            return message_data(None, None, args, kwargs)

        procs on all member updates (see discord.py documentation for what this means)

        args:
        coro (coroutine) = coroutine to run after function finishes running
        secondary_args:
        func (function) = function to run, returns a message_data
        """
        def wrap(func):
            def wrapper(before, after):
                return func(before, after)
            self.on_member_update_list[func.__name__] = funcblocker(
                wrapper, None, None, False, coro)
            return wrapper
        return wrap

    async def run_on_member_update(self, before, after):
        for func in self.on_member_update_list.values():
            message_info = func.simple_proc(before, after)
            message = await self.send_message(message_info)
            if func.coro is not None and message_info is not None:
                await func.coro(message, *message_info.args, **message_info.kwargs)

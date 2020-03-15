import discord


class message_data:
    def __init__(self, channel=None, message=None, embed=None, args=None, kwargs=None):
        """
        message_data is a container to be returned at the end of each YangBot function

        channel: channel to send message
        message: message to send, None if no message is sent
        args: list of arguments to send to a coroutine run after a function's completion
        kwargs: dictionary/map of arguments to send to a coroutine run after a function's completion
        """
        self.channel = channel
        self.message = message
        self.embed = discord.Embed(**embed) if embed is not None else None
        for item in embed['fields']:
            self.embed.add_field(name=item['name'],value=item['value'],inline=item['inline'])
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}

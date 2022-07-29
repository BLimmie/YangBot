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
        if embed is None:
            self.embed = None
        else:
            if 'fields' in embed:
                fields = embed['fields']
                del embed['fields'] # Deletes the pointer, NOT the object
            else:
                fields = []
            self.embed = discord.Embed(**embed)
            for item in fields:
                self.embed.add_field(name=item['name'],value=item['value'],inline=item['inline'] if 'inline' in item else False)

        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}

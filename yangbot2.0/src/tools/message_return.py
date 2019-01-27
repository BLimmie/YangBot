class message_data:
    def __init__(self, channel, message, args=[], kwargs={}):
        self.channel = channel
        self.message = message
        self.args = args
        self.kwargs = kwargs
class message_data:
    def __init__(self, channel, message, args=None):
        self.channel = channel
        self.message = message
        self.args = args
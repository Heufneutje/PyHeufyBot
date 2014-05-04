class IRCChannel(object):
    def __init__(self, name):
        self.name = name
        self.users = {}
        self.ranks = {}
        self.modes = {}
        self.topic = None
        self.topicSetter = None
        self.topicTimestamp = 0
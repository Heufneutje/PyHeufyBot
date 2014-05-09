class IRCChannel(object):
    def __init__(self, name):
        self.name = name
        self.users = {}
        self.ranks = {}
        self.modes = {}
        self.topic = None
        self.topicSetter = None
        self.topicTimestamp = 0
        self.creationTime = 0

        self.namesListComplete = True

    def getHighestRankOfUser(self, nickname, prefixOrder):
        if nickname not in self.ranks:
            return None

        for mode in prefixOrder:
            if mode in self.ranks[nickname]:
                return mode

        return None

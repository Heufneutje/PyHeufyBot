class IRCUser(object):
    def __init__(self, userString):
        exclamationIndex = userString.index("!")
        atIndex = userString.index("@")

        self.nickname = userString[:exclamationIndex]
        self.username = userString[exclamationIndex + 1:atIndex]
        self.hostname = userString[atIndex + 1:]
        self.realname = None
        self.server = None
        self.hops = 0
        self.oper = False
        self.away = False

    def getFullName(self):
        return "{}!{}@{}".format(self.nickname, self.username, self.hostname)
class IRCUser(object):
    def __init__(self, nickname, ident=None, host=None):
        self.nickname = nickname
        self.ident = ident
        self.host = host
        self.gecos = None
        self.server = None
        self.hops = 0
        self.isOper = False
        self.isAway = False

    def fullUserPrefix(self):
        return "{}!{}@{}".format(self.nickname, self.ident, self.host)

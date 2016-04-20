class IRCUser(object):
    def __init__(self, nick, ident=None, host=None):
        self.nick = nick
        self.ident = ident
        self.host = host
        self.gecos = None
        self.server = None
        self.hops = 0
        self.isOper = False
        self.isAway = False
        self.account = None

    def fullUserPrefix(self):
        return "{}!{}@{}".format(self.nick, self.ident, self.host)

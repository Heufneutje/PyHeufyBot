class OutputHandler(object):
    def __init__(self, connection):
        self.connection = connection

    def cmdJOIN(self, channel, key=""):
        if channel[0] not in self.connection.supportHelper.chanTypes:
            channel = "#{}".format(channel)
        self.connection.sendMessage("JOIN", channel, key)

    def cmdNAMES(self, channel):
        self.connection.sendMessage("NAMES", channel)

    def cmdNICK(self, nick):
        self.connection.sendMessage("NICK", nick)

    def cmdNOTICE(self, target, message):
        self.connection.sendMessage("NOTICE", target, ":{}".format(message))

    def cmdPASS(self, password):
        self.connection.sendMessage("PASS", ":{}".format(password))

    def cmdPING(self, message):
        self.connection.sendMessage("PING", ":{}".format(message))

    def cmdPRIVMSG(self, target, message):
        self.connection.sendMessage("PRIVMSG", target, ":{}".format(message))

    def cmdPONG(self, message):
        self.connection.sendMessage("PONG", ":{}".format(message))

    def cmdQUIT(self, reason):
        self.connection.sendMessage("QUIT", ":{}".format(reason))

    def cmdUSER(self, ident, gecos):
        # RFC2812 allows usermodes to be set, but this isn't implemented much in IRCds at all.
        # Pass 0 for usermodes instead.
        self.connection.sendMessage("USER", ident, "0", "*", ":{}".format(gecos))

    def cmdWHO(self, mask):
        if not mask:
            mask = "*"
        self.connection.sendMessage("WHO", mask)

class OutputHandler(object):
    def __init__(self, connection):
        self.connection = connection

    def cmdJOIN(self, channels, keys=None):
        chans = channels.split(",")
        for i in range(len(chans)):
            if chans[i][0] not in self.connection.supportHelper.chanTypes:
                chans[i] = "#{}".format(chans[i])
        channels = ",".join(chans)
        if keys:
            self.connection.sendMessage("JOIN", channels, keys)
        else:
            self.connection.sendMessage("JOIN", channels)

    def cmdNICK(self, nick):
        self.connection.sendMessage("NICK", nick)

    def cmdPING(self, message):
        self.connection.sendMessage("PING", ":{}".format(message))

    def cmdPONG(self, message):
        self.connection.sendMessage("PONG", ":{}".format(message))

    def cmdQUIT(self, reason):
        self.connection.sendMessage("QUIT", ":{}".format(reason))

    def cmdUSER(self, ident, gecos):
        # RFC2812 allows usermodes to be set, but this isn't implemented much in IRCds at all.
        # Pass 0 for usermodes instead.
        self.connection.sendMessage("USER", ident, "0", "*", ":{}".format(gecos))

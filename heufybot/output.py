class OutputHandler(object):
    def __init__(self, connection):
        self.connection = connection

    def cmdNICK(self, nick):
        self.connection.sendMessage("NICK", nick)

    def cmdUSER(self, ident, gecos):
        # RFC2812 allows usermodes to be set, but this isn't implemented much in IRCds at all.
        # Pass 0 for usermodes instead.
        self.connection.sendMessage("USER", ident, "0", "*", ":{}".format(gecos))

    def cmdQUIT(self, reason):
        self.connection.sendMessage("QUIT", ":{}".format(reason))

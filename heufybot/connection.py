from twisted.words.protocols import irc


class HeufyBotConnection(irc.IRC):
    def __init__(self, protocol):
        self.protocol = protocol
        self.nick = "PyHeufyBot"  # TODO This will be set by a configuration at some point
        self.ident = "PyHeufyBot"  # TODO This will be set by a configuration at some point
        self.gecos = "PyHeufyBot IRC Bot"  # TODO This will be set by a configuration at some point
        self.channels = {}
        self.usermodes = {}

    def connectionMade(self):
        self.cmdNICK(self.nick)
        self.cmdUSER(self.ident, self.gecos)

    def handleCommand(self, command, prefix, params):
        print prefix, command, " ".join(params)

    def sendMessage(self, command, *parameter_list, **prefix):
        print command, " ".join(parameter_list)
        irc.IRC.sendMessage(self, command, *parameter_list, **prefix)

    def cmdNICK(self, nick):
        self.sendMessage("NICK", nick)

    def cmdUSER(self, ident, gecos):
        # RFC2812 allows usermodes to be set, but this isn't implemented much in IRCds at all.
        # Pass 0 for usermodes instead.
        self.sendMessage("USER", ident, "0", "*", ":{}".format(gecos))

    def cmdQUIT(self, reason):
        self.sendMessage("QUIT", ":{}".format(reason))

    def disconnect(self, reason="Quitting...", fullDisconnect = False):
        # TODO: Find a better solution to full disconnects
        self.cmdQUIT(reason)
        self.transport.fullDisconnect = fullDisconnect
        self.transport.loseConnection()

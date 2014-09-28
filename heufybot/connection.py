from twisted.words.protocols import irc


class HeufyBotConnection(irc.IRC):
    def __init__(self, protocol):
        self.protocol = protocol
        self.nickname = "PyHeufyBot" #TODO This will be set by a configuration at some point
        self.ident = "PyHeufyBot" #TODO This will be set by a configuration at some point
        self.gecos = "PyHeufyBot IRC Bot" #TODO This will be set by a configuration at some point

    def connectionMade(self):
        self.cmdNICK(self.nickname)
        self.cmdUSER(self.ident, self.gecos)

    def connectionLost(self, reason=""):
        print reason

    def dataReceived(self, data):
        print data

    def sendMessage(self, command, *parameter_list, **prefix):
        print command, " ".join(parameter_list)
        irc.IRC.sendMessage(self, command, *parameter_list, **prefix)

    def cmdNICK(self, nickname):
        self.sendMessage("NICK", nickname)

    def cmdUSER(self, ident, gecos):
        # RFC2812 allows usermodes to be set, but this isn't implemented much in IRCds at all.
        # Pass 0 for usermodes instead.
        self.sendMessage("USER", ident, "0", "*", ":{}".format(gecos))

from twisted.words.protocols import irc


class HeufyBotConnection(irc.IRC):
    def __init__(self, protocol):
        self.protocol = protocol
        self.nickname = "PyHeufyBot" #TODO This will be set by a configuration at some point
        self.ident = "PyHeufyBot" #TODO This will be set by a configuration at some point
        self.gecos = "PyHeufyBot IRC Bot" #TODO This will be set by a configuration at some point

    def connectionMade(self):
        self.sendMessage("NICK", "PyHeufyBot")
        self.sendMessage("USER", "PyHeufyBot", "0", "0", ":PyHeufyBot Bot")
        print "OK"

    def connectionLost(self, reason=""):
        print reason

    def dataReceived(self, data):
        print data
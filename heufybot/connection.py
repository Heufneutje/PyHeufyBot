from twisted.words.protocols import irc


class HeufyBotConnection(irc.IRC):
    def __init__(self, protocol):
        self.protocol = protocol

    def connectionMade(self):
        self.sendLine("NICK PyHeufyBot")
        self.sendLine("USER PyHeufyBot 0 0 :PyHeufyBot")
        print "OK"

    def connectionLost(self, reason=""):
        print reason

    def dataReceived(self, data):
        print data
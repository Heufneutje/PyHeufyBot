from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from globalvars import version
from config import Config

class HeufyBot(irc.IRCClient):
    nickname = None
    username = None
    realname = None
    factory = None

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.nickname = self.factory.config.settings["nickname"]
        self.username = self.factory.config.settings["username"]
        self.realname = self.factory.config.settings["realname"]

class HeufyBotFactory(protocol.ReconnectingClientFactory):
    protocol = HeufyBot
    bot = None
    config = None

    def __init__(self, config):
        self.config = config

    def startedConnecting(self, connector):
        print "*** Connecting to server..."

    def buildProtocol(self, addr):
        print "*** Connected."
        print "*** Resetting reconnection delay..."
        self.resetDelay()

        bot = HeufyBot(self)
        return bot

    def clientConnectionLost(self, connector, reason):
        print "*** Connection lost. (Reason: {})".format(reason)
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
       print "*** Connection failed. (Reason: {})".format(reason)
       protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

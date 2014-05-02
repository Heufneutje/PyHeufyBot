from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from globalvars import version
from config import Config

class HeufyBot(irc.IRCClient):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.nickname = self.factory.config.settings["nickname"]
        self.username = self.factory.config.settings["username"]
        self.realname = self.factory.config.settings["realname"]
        irc.IRCClient.connectionMade(self)
        
        print "--- Connected to {}.".format(self.factory.config.getSettingWithDefault("server", "irc.foo.bar"))
        print "--- Resetting reconnection delay..."
        self.factory.resetDelay()

    def lineReceived(self, line):
        #print line
        pass

class HeufyBotFactory(protocol.ReconnectingClientFactory):
    def __init__(self, config):
        self.config = config
        self.protocol = HeufyBot

    def startedConnecting(self, connector):
        print "--- Connecting to server {}...".format(self.config.getSettingWithDefault("server", "irc.foo.bar"))

    def buildProtocol(self, addr):
        self.bot = HeufyBot(self)
        return self.bot

    def clientConnectionLost(self, connector, reason):
        print "*** Connection lost. (Reason: {})".format(reason)
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print "*** Connection failed. (Reason: {})".format(reason)
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

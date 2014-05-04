from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from pyheufybot.globalvars import version
from pyheufybot.config import Config
from pyheufybot.user import IRCUser
from pyheufybot.logger import log

class HeufyBot(irc.IRCClient):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.nickname = self.factory.config.settings["nickname"]
        self.username = self.factory.config.settings["username"]
        self.realname = self.factory.config.settings["realname"]
        irc.IRCClient.connectionMade(self)
        
        log("--- Connected to {}.".format(self.factory.config.getSettingWithDefault("server", "irc.foo.bar")), None)
        log("--- Resetting reconnection delay...", None)
        self.factory.resetDelay()

    def irc_JOIN(self, prefix, params):
        user = IRCUser(prefix)

class HeufyBotFactory(protocol.ReconnectingClientFactory):
    protocol = HeufyBot
    
    def __init__(self, config):
        self.config = config

    def startedConnecting(self, connector):
        log("--- Connecting to server {}...".format(self.config.getSettingWithDefault("server", "irc.foo.bar")), None)

    def buildProtocol(self, addr):
        self.bot = HeufyBot(self)
        return self.bot

    def clientConnectionLost(self, connector, reason):
        log("*** Connection lost. (Reason: {})".format(reason), None)
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        log("*** Connection failed. (Reason: {})".format(reason), None)
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
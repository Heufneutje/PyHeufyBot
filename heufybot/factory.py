from twisted.internet.protocol import ClientFactory, ReconnectingClientFactory
from twisted.python import log
from heufybot.connection import HeufyBotConnection


class HeufyBotFactory(ReconnectingClientFactory):
    protocol = HeufyBotConnection

    def __init__(self, bot):
        self.bot = bot
        self.currentlyDisconnecting = []

    def buildProtocol(self, addr):
        self.resetDelay()
        return self.protocol(self.bot)

    def clientConnectionFailed(self, connector, reason):
        log.msg("Client connection to {} failed (Reason: {}).".format(connector.host, reason.value))
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        # Disable modules
        if connector.host in self.bot.moduleHandler.enabledModules:
            del self.bot.moduleHandler.enabledModules[connector.host]

        del self.bot.servers[connector.host]

        # Check whether or not we should reconnect
        if connector.host in self.currentlyDisconnecting:
            log.msg("Connection to {} was closed cleanly.".format(connector.host))
            ClientFactory.clientConnectionLost(self, connector, reason)
            self.currentlyDisconnecting.remove(connector.host)
            self.bot.countConnections()
        else:
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

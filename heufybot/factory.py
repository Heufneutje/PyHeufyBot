from twisted.internet.protocol import ClientFactory, ReconnectingClientFactory
from heufybot.connection import HeufyBotConnection


class HeufyBotFactory(ReconnectingClientFactory):
    protocol = HeufyBotConnection

    def __init__(self, bot):
        self.bot = bot

    def buildProtocol(self, addr):
        return self.protocol(self)

    def clientConnectionLost(self, connector, reason):
        if connector.transport.fullDisconnect:
            ClientFactory.clientConnectionLost(self, connector, reason)
        else:
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
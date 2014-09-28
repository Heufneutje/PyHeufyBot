from twisted.internet.protocol import ReconnectingClientFactory
from heufybot.connection import HeufyBotConnection


class HeufyBotFactory(ReconnectingClientFactory):
    protocol = HeufyBotConnection

    def __init__(self, bot):
        self.bot = bot

    def buildProtocol(self, addr):
        return self.protocol(self)

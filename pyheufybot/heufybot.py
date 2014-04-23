from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from sys import stdout
import os

class HeufyBot(irc.IRCClient):
    nickname = "PyHeufyBot"
    username = "HeufyBot"
    realname = "PyHeufyBot V0.0.1"

class HeufyBotFactory(protocol.ReconnectingClientFactory):
    protocol = HeufyBot

    def startedConnecting(self, connector):
        log.msg("*** Connecting to server...")

    def buildProtocol(self, addr):
        log.msg("*** Connected.")
        log.msg("*** Resetting reconnection delay...")
        self.resetDelay()
        return HeufyBot()

    def clientConnectionLost(self, connector, reason):
        log.msg("*** Connection lost. (Reason: {}".format(reason))
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        log.msg("*** Connection failed. (Reason: {}".format(reason))
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

if __name__ == '__main__':
    heufybot = HeufyBotFactory()

    log.startLogging(stdout)
    log.addObserver(log.FileLogObserver(open(os.path.join("logs/debug.log"), "a")).emit)

    reactor.connectTCP("localhost", 6667, heufybot)
    reactor.run()

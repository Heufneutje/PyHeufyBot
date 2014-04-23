from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

class HeufyBot(irc.IRCClient):
    nickname = "PyHeufyBot"
    username = "HeufyBot"
    realname = "PyHeufyBot V0.0.1"

class HeufyBotFactory(protocol.ReconnectingClientFactory):
    protocol = HeufyBot

    def startedConnecting(self, connector):
        print "*** Connecting to server..."

    def buildProtocol(self, addr):
        print "*** Connected."
        print "*** Resetting reconnection delay..."
        self.resetDelay()
        return HeufyBot()

    def clientConnectionLost(self, connector, reason):
        print "*** Connection lost. (Reason: {}".format(reason)
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
       print "*** Connection failed. (Reason: {}".format(reason)
       protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

if __name__ == '__main__':
    heufybot = HeufyBotFactory()

    reactor.connectTCP("localhost", 6667, heufybot)
    reactor.run()

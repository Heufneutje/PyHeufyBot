from twisted.words.protocols import irc
from twisted.python import log
import logging


class HeufyBotConnection(irc.IRC):
    def __init__(self, bot):
        self.bot = bot
        self.name = None
        self.nick = "PyHeufyBot"  # TODO This will be set by a configuration at some point
        self.ident = "PyHeufyBot"  # TODO This will be set by a configuration at some point
        self.gecos = "PyHeufyBot IRC Bot"  # TODO This will be set by a configuration at some point
        self.channels = {}
        self.usermodes = {}

    def connectionMade(self):
        self.name = self.transport.addr[0]
        self.transport.fullDisconnect = False
        self.bot.servers[self.name] = self
        self.cmdNICK(self.nick)
        self.cmdUSER(self.ident, self.gecos)

    def handleCommand(self, command, prefix, params):
        log.msg(prefix, command, " ".join(params), level=logging.DEBUG)

    def sendMessage(self, command, *parameter_list, **prefix):
        log.msg(command, " ".join(parameter_list), level=logging.DEBUG)
        irc.IRC.sendMessage(self, command, *parameter_list, **prefix)

    def cmdNICK(self, nick):
        self.sendMessage("NICK", nick)

    def cmdUSER(self, ident, gecos):
        # RFC2812 allows usermodes to be set, but this isn't implemented much in IRCds at all.
        # Pass 0 for usermodes instead.
        self.sendMessage("USER", ident, "0", "*", ":{}".format(gecos))

    def cmdQUIT(self, reason):
        self.sendMessage("QUIT", ":{}".format(reason))

    def disconnect(self, reason="Quitting...", fullDisconnect = False):
        # TODO: Find a better solution to full disconnects
        self.cmdQUIT(reason)
        self.transport.fullDisconnect = fullDisconnect
        self.transport.loseConnection()

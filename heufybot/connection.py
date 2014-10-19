from twisted.words.protocols import irc
from twisted.python import log as twistedlog
from heufybot.input import InputHandler
import logging


class HeufyBotConnection(irc.IRC):
    def __init__(self, bot):
        self.bot = bot
        self.inputHandler = InputHandler(self)
        self.loggedIn = False
        self.name = None
        self.nick = None
        self.ident = None
        self.gecos = None
        self.channels = {}
        self.usermodes = {}

    def connectionMade(self):
        # Connection finalizing
        self.name = self.transport.addr[0]
        self.log("Connection established.")
        self.transport.fullDisconnect = False
        self.bot.servers[self.name] = self

        # Start logging in
        self.nick = self.bot.config.serverItemWithDefault(self.name, "nickname", "HeufyBot")
        self.ident = self.bot.config.serverItemWithDefault(self.name, "username", self.nick)
        self.gecos = self.bot.config.serverItemWithDefault(self.name, "realname", self.nick)
        self.log("Logging in as {}!{} :{}...".format(self.nick, self.ident, self.gecos))
        self.cmdNICK(self.nick)
        self.cmdUSER(self.ident, self.gecos)

    def handleCommand(self, command, prefix, params):
        self.log(prefix, command, " ".join(params), level=logging.DEBUG)
        self.inputParser.handleCommand(command, prefix, params)

    def sendMessage(self, command, *parameter_list, **prefix):
        self.log(command, " ".join(parameter_list), level=logging.DEBUG)
        irc.IRC.sendMessage(self, command, *parameter_list, **prefix)

    def log(self, *message, **kw):
        if "level" in kw:
            twistedlog.msg("[{}] {}".format(self.name, " ".join(message)), level=kw["level"])
        else:
            twistedlog.msg("[{}] {}".format(self.name, " ".join(message)))

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

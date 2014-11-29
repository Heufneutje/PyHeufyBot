from twisted.words.protocols import irc
from twisted.python import log as twistedlog
from heufybot.input import InputHandler
from heufybot.output import OutputHandler
from heufybot.supported import ISupport
from weakref import WeakValueDictionary
import logging


class HeufyBotConnection(irc.IRC):
    def __init__(self, bot):
        self.bot = bot
        self.inputHandler = InputHandler(self)
        self.outputHandler = OutputHandler(self)
        self.supportHelper = ISupport()
        self.loggedIn = False
        self.name = None
        self.nick = None
        self.ident = None
        self.gecos = None
        self.channels = {}
        self.users = WeakValueDictionary()
        self.usermodes = {}

    def connectionMade(self):
        self.bot.moduleHandler.runGenericAction("connect", self.name)

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
        self.outputHandler.cmdNICK(self.nick)
        password = self.bot.config.serverItemWithDefault(self.name, "password", None)
        if password:
            self.outputHandler.cmdPASS(password)
        self.outputHandler.cmdUSER(self.ident, self.gecos)

    def handleCommand(self, command, prefix, params):
        self.bot.moduleHandler.runGenericAction("receivecommand-{}".format(command), params)
        self.log(prefix, command, " ".join(params), level=logging.DEBUG)
        self.inputHandler.handleCommand(command, prefix, params)

    def sendMessage(self, command, *parameter_list, **prefix):
        self.bot.moduleHandler.runGenericAction("sendcommand-{}".format(command), *parameter_list)
        self.log(command, " ".join(parameter_list), level=logging.DEBUG)
        irc.IRC.sendMessage(self, command, *parameter_list, **prefix)

    def log(self, *message, **kw):
        if "level" in kw:
            twistedlog.msg("[{}] {}".format(self.name, " ".join(message)), level=kw["level"])
        else:
            twistedlog.msg("[{}] {}".format(self.name, " ".join(message)))

    def disconnect(self, reason="Quitting...", fullDisconnect = False):
        # TODO: Find a better solution to full disconnects
        self.outputHandler.cmdQUIT(reason)
        self.transport.fullDisconnect = fullDisconnect
        self.transport.loseConnection()

from twisted.internet.interfaces import ISSLTransport
from heufybot.ircbase import IRCBase
from heufybot.input import InputHandler
from heufybot.output import OutputHandler
from heufybot.supported import ISupport
from heufybot.utils import isNumber
from weakref import WeakValueDictionary


class HeufyBotConnection(IRCBase):
    def __init__(self, bot):
        self.bot = bot
        self.inputHandler = InputHandler(self)
        self.outputHandler = OutputHandler(self)
        self.supportHelper = ISupport()
        self.loggedIn = False
        self.secureConnection = False
        self.name = None
        self.nick = None
        self.ident = None
        self.gecos = None
        self.channels = {}
        self.users = WeakValueDictionary()
        self.userModes = {}

    def connectionMade(self):
        self.bot.moduleHandler.runGenericAction("connect", self.name)

        # Connection finalizing.
        if ISSLTransport.providedBy(self.transport):
            self.secureConnection = True

        self.name = self.transport.addr[0]
        self.bot.log.info("[{connection}] Connection established.", connection=self.name)
        self.supportHelper.network = self.name
        self.bot.servers[self.name] = self

        # Enable modules.
        self.bot.moduleHandler.enableModulesForServer(self.name)

        # Initialize login data from the config.
        self.nick = self.bot.config.serverItemWithDefault(self.name, "nickname", "HeufyBot")
        self.ident = self.bot.config.serverItemWithDefault(self.name, "username", self.nick)
        self.gecos = self.bot.config.serverItemWithDefault(self.name, "realname", self.nick)

        # Send a server password if defined.
        password = self.bot.config.serverItemWithDefault(self.name, "password", None)
        if password:
            self.bot.log.info("[{connection}] Sending network password...", connection=self.name)
            self.outputHandler.cmdPASS(password)

        # Start logging in.
        self.bot.moduleHandler.runGenericAction("prelogin", self.name)
        self.bot.log.info("[{connection}] Logging in as {nick}!{ident} :{gecos}...", connection=self.name,
                          nick=self.nick, ident=self.ident, gecos=self.gecos)
        self.outputHandler.cmdNICK(self.nick)
        self.outputHandler.cmdUSER(self.ident, self.gecos)

    def handleCommand(self, command, params, prefix, tags):
        self.bot.log.debug("[{connection}] {tags} {prefix} {command} {params}", connection=self.name,
                           tags=tags, prefix=prefix, command=command, params=" ".join(params))
        if isNumber(command):
            self.inputHandler.handleNumeric(command, prefix, params)
        else:
            self.inputHandler.handleCommand(command, prefix, params)

    def sendMessage(self, command, *parameter_list, **prefix):
        self.bot.moduleHandler.runGenericAction("sendcommand-{}".format(command), self.name, *parameter_list)
        self.bot.log.debug("[{connection}] {command} {params}",
                           connection=self.name, command=command, params=" ".join(parameter_list))
        IRCBase.sendMessage(self, command, *parameter_list, **prefix)

    def disconnect(self, reason = "Quitting...", fullDisconnect = False):
        if fullDisconnect:
            self.bot.connectionFactory.currentlyDisconnecting.append(self.name)
        self.outputHandler.cmdQUIT(reason)
        self.transport.loseConnection()

    def setUserModes(self, modes):
        adding = True
        modesAdded = []
        modesRemoved = []
        for mode in modes:
            if mode == "+":
                adding = True
            elif mode == "-":
                adding = False
            elif mode not in self.supportHelper.userModes:
                self.bot.warn("[{connection}] Received unknown MODE char {mode} in MODE string {modes}.",
                              connection=self.name, mode=mode, modes=modes)
                return None
            elif adding:
                self.userModes[mode] = None
                modesAdded.append(mode)
            elif not adding and mode in self.userModes:
                del self.userModes[mode]
                modesRemoved.append(mode)
        return {
            "added": modesAdded,
            "removed": modesRemoved
        }

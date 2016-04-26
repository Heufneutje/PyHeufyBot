from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements
from base64 import b64encode


class IRCv3SASL(BotModule):
    implements(IPlugin, IBotModule)

    name = "SASL"
    capName = "sasl"
    config = {}

    def actions(self):
        return [ ("listcaps", 1, self.initAndAddToCapList),
                 ("caps-acknowledged", 1, self.requestNegotiation),
                 ("pre-handlecommand-AUTHENTICATE", 1, self.authenticate),
                 ("pre-handlenumeric-900", 1, self.handleSuccessReply),
                 ("pre-handlenumeric-902", 1, self.handleFailureReply),
                 ("pre-handlenumeric-903", 1, self.handleSuccessReply),
                 ("pre-handlenumeric-904", 1, self.handleFailureReply),
                 ("pre-handlenumeric-905", 1, self.handleFailureReply),
                 ("pre-handlenumeric-907", 1, self.handleFailureReply) ]

    def initAndAddToCapList(self, server, caps):
        username = self.bot.config.serverItemWithDefault(server, "sasl_username", None)
        if not username:
            self.bot.log.warn("[{server}] No SASL username found. SASL cap will not be requested.", server=server)
            return

        password = self.bot.config.serverItemWithDefault(server, "sasl_password", None)
        if not password:
            self.bot.log.warn("[{server}] No SASL password found. SASL cap will not be requested.", server=server)
            return

        self.config[server] = {
            "username": username,
            "password": password,
            "mechanism": self.bot.config.serverItemWithDefault(server, "sasl_mechanism", "PLAIN")
        }

        caps.append(self.capName)

    def requestNegotiation(self, server, caps):
        if self.capName in caps:
            self.bot.log.info("[{server}] Attempting SASL authentication...", server=server)
            self.bot.servers[server].sendMessage("AUTHENTICATE", self.config[server]["mechanism"])

    def authenticate(self, server, nick, ident, host, params):
        if params[0] == "+":
            if self.config[server]["mechanism"] == "PLAIN":
                self._handlePLAIN(server)
        return True

    def handleSuccessReply(self, server, prefix, params):
        self.bot.log.info("[{server}] {message}", server=server, message=params[1])
        self.bot.moduleHandler.runGenericAction("cap-handler-finished", server, self.capName)
        return True

    def handleFailureReply(self, server, prefix, params):
        self.bot.warn.info("[{server}] {message}", server=server, message=params[1])
        self.bot.moduleHandler.runGenericAction("cap-handler-finished", server, self.capName)
        return True

    def _handlePLAIN(self, server):
        authString = b64encode(self.config[server]["username"] + u"\u0000" + self.config[server]["username"] + \
                               u"\u0000" + self.config[server]["password"])
        self.bot.servers[server].sendMessage("AUTHENTICATE", authString)


saslModule = IRCv3SASL()

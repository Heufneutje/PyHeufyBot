from twisted.internet.interfaces import ISSLTransport
from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements

try:
    from twisted.internet import ssl
except ImportError:
    ssl = None


class IRCv3StartTLS(BotModule):
    implements(IPlugin, IBotModule)

    name = "StartTLS"
    core = True
    capName = "tls"

    def actions(self):
        return [ ("listcaps", 1, self.addToCapList),
                 ("caps-acknowledged", 1, self.requestNegotiation),
                 ("pre-handlenumeric-670", 1, self.startNegotiation),
                 ("pre-handlenumeric-691", 1, self.negotiationFailed) ]

    def addToCapList(self, server, caps):
        if not self.bot.servers[server].secureConnection and ssl is not None:
            caps.append(self.capName)

    def requestNegotiation(self, server, caps):
        if self.capName in caps:
            self.bot.log.info("[{server}] Trying to initiate StartTLS...", server=server)
            self.bot.servers[server].sendMessage("STARTTLS")

    def startNegotiation(self, server, prefix, params):
        self.bot.log.info("[{server}] Server replied: \"{reply}\"", server=server, reply=params[1])
        self.bot.log.info("[{server}] Proceeding with TLS handshake...", server=server)
        self.bot.servers[server].transport.startTLS(ssl.CertificateOptions())
        if ISSLTransport.providedBy(self.bot.servers[server].transport):
            self.bot.servers[server].secureConnection = True
        self.bot.log.info("[{server}] TLS handshake successful. Connection is now secure.", server=server)
        self.bot.moduleHandler.runGenericAction("cap-handler-finished", server, self.capName)
        return True

    def negotiationFailed(self, server, prefix, params):
        self.bot.log.warn("[{server}] StartTLS failed, reason: \"{reply}\".", server=server, reply=params[1])
        self.bot.moduleHandler.runGenericAction("cap-handler-finished", server, self.capName)
        return True


startTLS = IRCv3StartTLS()

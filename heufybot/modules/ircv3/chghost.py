from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class IRCv3ChgHost(BotModule):
    implements(IPlugin, IBotModule)

    name = "ChgHost"
    capName = "chghost"
    core = True

    def actions(self):
        return [ ("listcaps", 1, self.addToCapList),
                 ("pre-handlecommand-CHGHOST", 1, self.handleChgHost),
                 ("caps-acknowledged", 1, self.finishHandler) ]

    def addToCapList(self, server, caps):
        caps.append(self.capName)

    def handleChgHost(self, server, nick, ident, host, params):
        if not self.bot.moduleHandler.runActionUntilTrue("has-cap-enabled", server, self.capName):
            return False

        if nick not in self.bot.servers[server].users:
            self.bot.log.warn("[{server}] Received CHGHOST message for unknown user {nick}", server=server, nick=nick)
            return False

        user = self.bot.servers[server].users[nick]
        user.ident = params[0]
        user.host = params[1]

        return False

    def finishHandler(self, server, caps):
        if self.capName in caps:
            self.bot.moduleHandler.runGenericAction("cap-handler-finished", server, self.capName)


chghost = IRCv3ChgHost()

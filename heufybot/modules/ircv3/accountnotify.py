from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class IRCv3AccountNotify(BotModule):
    implements(IPlugin, IBotModule)

    name = "AccountNotify"
    capName = "account-notify"

    def actions(self):
        return [ ("listcaps", 1, self.addToCapList),
                 ("pre-handlecommand-ACCOUNT", 1, self.handleAccountNotify),
                 ("caps-acknowledged", 1, self.finishHandler) ]

    def addToCapList(self, server, caps):
        caps.append(self.capName)

    def handleAccountNotify(self, server, nick, ident, host, params):
        if not self.bot.moduleHandler.runActionUntilTrue("has-cap-enabled", server, self.capName):
            return False

        if nick not in self.bot.servers[server].users:
            self.bot.log.warn("[{server}] Received ACCOUNT message for unknown user {nick}", server=server, nick=nick)
            return False

        user = self.bot.servers[server].users[nick]
        if params[0] == "*":
            user.account = None
        else:
            user.account = params[0]

        return False

    def finishHandler(self, server, caps):
        if self.capName in caps:
            self.bot.moduleHandler.runGenericAction("cap-handler-finished", server, self.capName)


accountNotify = IRCv3AccountNotify()

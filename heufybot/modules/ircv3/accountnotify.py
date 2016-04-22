from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class IRCv3AccountNotify(BotModule):
    implements(IPlugin, IBotModule)

    name = "AccountNotify"

    def actions(self):
        return [ ("listcaps", 1, self.addToCapList),
                 ("pre-handlecommand-ACCOUNT", 1, self.handleAccountNotify) ]

    def addToCapList(self, server, caps):
        caps.append("account-notify")

    def handleAccountNotify(self, server, nick, ident, host, params):
        if not self.bot.moduleHandler.runActionUntilTrue("hascapenabled", server, "account-notify"):
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


accountNotify = IRCv3AccountNotify()

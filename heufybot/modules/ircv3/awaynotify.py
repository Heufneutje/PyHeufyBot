from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class IRCv3AwayNotify(BotModule):
    implements(IPlugin, IBotModule)

    name = "AwayNotify"
    capName = "away-notify"

    def actions(self):
        return [ ("listcaps", 1, self.addToCapList),
                 ("pre-handlecommand-AWAY", 1, self.handleAwayNotify),
                 ("caps-acknowledged", 1, self.finishHandler) ]

    def addToCapList(self, server, caps):
        caps.append(self.capName)

    def handleAwayNotify(self, server, nick, ident, host, params):
        if not self.bot.moduleHandler.runActionUntilTrue("has-cap-enabled", server, self.capName):
            return False

        if nick not in self.bot.servers[server].users:
            self.bot.log.warn("[{server}] Received AWAY message for unknown user {nick}", server=server, nick=nick)
            return False

        user = self.bot.servers[server].users[nick]
        if len(params) == 1:
            user.isAway = True
            user.awayMessage = params[0]
        else:
            user.isAway = False
            user.awayMessage = None

        return False

    def finishHandler(self, server, caps):
        if self.capName in caps:
            self.bot.moduleHandler.runGenericAction("cap-handler-finished", server, self.capName)


awayNotify = IRCv3AwayNotify()

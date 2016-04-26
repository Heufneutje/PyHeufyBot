from twisted.plugin import IPlugin
from heufybot.channel import IRCChannel
from heufybot.moduleinterface import BotModule, IBotModule
from heufybot.user import IRCUser
from zope.interface import implements


class IRCv3ExtendedJoin(BotModule):
    implements(IPlugin, IBotModule)

    name = "ExtendedJoin"
    capName = "extended-join"

    def actions(self):
        return [ ("listcaps", 1, self.addToCapList),
                 ("pre-handlecommand-JOIN", 1, self.handleExtendedJoin),
                 ("caps-acknowledged", 1, self.finishHandler) ]

    def addToCapList(self, server, caps):
        caps.append(self.capName)

    def handleExtendedJoin(self, server, nick, ident, host, params):
        if not self.bot.moduleHandler.runActionUntilTrue("has-cap-enabled", server,self.capName):
            return False

        if nick not in self.bot.servers[server].users:
            user = IRCUser(nick, ident, host)
            if params[1] != "*":
                user.account = params[1]
            user.gecos = params[2]
            self.bot.servers[server].users[nick] = user
        else:
            user = self.bot.servers[server].users[nick]
        if params[0] not in self.bot.servers[server].channels:
            channel = IRCChannel(params[0], self.bot.servers[server])
            self.bot.servers[server].outputHandler.cmdWHO(params[0])
            self.bot.servers[server].outputHandler.cmdMODE(params[0])
            self.bot.servers[server].channels[params[0]] = channel
        else:
            channel = self.bot.servers[server].channels[params[0]]
        channel.users[nick] = user
        channel.ranks[nick] = ""
        self.bot.moduleHandler.runGenericAction("channeljoin", self.bot.servers[server].name, channel, user)
        return True  # Override the core JOIN handler

    def finishHandler(self, server, caps):
        if self.capName in caps:
            self.bot.moduleHandler.runGenericAction("cap-handler-finished", server, self.capName)


extendedJoin = IRCv3ExtendedJoin()

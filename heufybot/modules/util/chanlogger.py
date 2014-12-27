from twisted.plugin import IPlugin
from heufybot.channel import IRCChannel
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements
import os, time


class ChannelLogger(BotModule):
    implements(IPlugin, IBotModule)

    name = "ChannelLogger"

    def hookBot(self, bot):
        self.bot = bot

    def actions(self):
        return [ ("ctcp-message", 100, self.logCTCP_ACTION),
                 ("channeljoin", 100, self.logJOIN),
                 ("channelkick", 100, self.logKICK),
                 ("modeschanged-channel", 100, self.logMODE),
                 ("changenick", 100, self.logNICK),
                 ("notice-channel", 100, self.logNOTICE),
                 ("channelpart", 100, self.logPART),
                 ("message-channel", 100, self.logPRIVMSG),
                 ("userquit", 100, self.logQUIT),
                 ("changetopic", 100, self.logTOPIC) ]

    def logCTCP_ACTION(self, server, source, user, body):
        if not isinstance(source, IRCChannel):
            return
        if not body.upper().startswith("ACTION"):
            return
        message = "* {} {}".format(user.nick, body[7:])
        self._writeLog(server, source.name, message)

    def logJOIN(self, server, channel, user):
        message = ">> {} ({}@{}) has joined {}".format(user.nick, user.ident, user.host, channel.name)
        self._writeLog(server, channel.name, message)

    def logKICK(self, server, channel, kicker, kicked, reason):
        message = "-- {} was kicked from {} by {} ({})".format(kicked.nick, channel.name, kicker.nick, reason)
        self._writeLog(server, channel.name, message)

    def logMODE(self, server, user, channel, modes, params, adding):
        operation = "+" if adding else "-"
        message = "-- {} sets mode: {}{} {}".format(user.nick, operation, "".join(modes), " ".join(params))
        self._writeLog(server, channel.name, message)

    def logNICK(self, server, user, nick, newnick):
        message = "-- {} is now known as {}".format(nick, newnick)
        for channel in self.bot.servers[server].channels.itervalues():
            if user.nick in channel.users:
                self._writeLog(server, channel.name, message)

    def logNOTICE(self, server, channel, user, body):
        message = "[NOTICE] --{}-- [{}] {}".format(user.nick, channel.name, body)
        self._writeLog(server, channel.name, message)

    def logPART(self, server, channel, user, reason):
        if reason:
            message = "<< {} ({}@{}) has left {} ({})".format(user.nick, user.ident, user.host, channel.name, reason)
        else:
            message = "<< {} ({}@{}) has left {}".format(user.nick, user.ident, user.host, channel.name)
        self._writeLog(server, channel.name, message)

    def logPRIVMSG(self, server, channel, user, body):
        message = "<{}{}> {}".format(channel.getHighestStatusOfUser(user), user.nick, body)
        self._writeLog(server, channel.name, message)

    def logQUIT(self, server, user, reason):
        if reason:
            message = "<< {} ({}@{}) has quit IRC ({})".format(user.nick, user.ident, user.host, reason)
        else:
            message = "<< {} ({}@{}) has quit IRC".format(user.nick, user.ident, user.host)
        for channel in self.bot.servers[server].channels.itervalues():
            if user.nick in channel.users:
                self._writeLog(server, channel.name, message)

    def logTOPIC(self, server, channel, user, oldTopic, newTopic):
        message = "-- {} changes topic to '{}'".format(user.nick, newTopic)
        self._writeLog(server, channel.name, message)

    def _writeLog(self, server, target, message):
        basePath = self.bot.config.serverItemWithDefault(server, "logpath", "logs")
        todayDate = time.strftime("%Y-%m-%d")
        todayTime = time.strftime("%H:%M:%S")
        if self.bot.servers[server].supportHelper.network:
            network = self.bot.servers[server].supportHelper.network
        else:
            network = server
        logPath = os.path.join(basePath, network, target, "{}.log".format(todayDate))
        if not os.path.exists(os.path.join(basePath, network, target)):
            os.makedirs(os.path.join(basePath, network, target))
        with open(logPath, "a+") as logFile:
            logFile.write("[{}] {}\n".format(todayTime, message))


chanLogger = ChannelLogger()

from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements
from datetime import date, timedelta
import os


class LogCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Log"

    def triggers(self):
        return ["log"]

    def load(self):
        self.help = "Commands: log (<YYYY-MM-DD>/-<numberofdays>) | Provides a log of the current channel for " \
                    "today, or another date if specified."
        self.commandHelp = {}

    def execute(self, server, source, command, params, data):
        if "channel" not in data:
            self.replyPRIVMSG(server, source, "I don't keep logs for private messages.")
            return

        basePath = self.bot.config.serverItemWithDefault(server, "logpath", "logs")
        error = "The date specified is invalid. Make sure you use -<numberofdays>, <yyyy/mm/dd>, or <yyyy-mm-dd>."
        network = self.bot.servers[server].supportHelper.network

        if len(params) < 1:
            logDate = date.today()
        elif params[0].startswith("-"):
            try:
                delta = int(params[0][1:])
            except ValueError:
                self.replyPRIVMSG(server, source, error)
                return
            logDate = date.today() - timedelta(delta)
        else:
            try:
                for symbol in ["/", "-"]:
                    if symbol in params[0]:
                        formattedDate = params[0].split(symbol)
                        logDate = date(int(formattedDate[0]), int(formattedDate[1]), int(formattedDate[2]))
                        break
                if logDate is None:
                    self.replyPRIVMSG(server, source, error)
                    return
            except (IndexError, ValueError):
                self.replyPRIVMSG(server, source, error)
                return

        strLogDate = logDate.strftime("%Y-%m-%d")
        logPath = os.path.join(basePath, network, source, "{}.log".format(strLogDate))
        if not os.path.exists(logPath):
            self.replyPRIVMSG(server, source, "I don't have that log.")
            return

        baseUrl = self.bot.config.serverItemWithDefault(server, "logurl", "irc.example.com")
        url = "{}?channel={}&network={}&date={}".format(baseUrl, source[1:], network, strLogDate)
        shortUrl = self.bot.moduleHandler.runActionUntilValue("shorten-url", url)
        if not shortUrl:
            shortUrl = url
        self.replyPRIVMSG(server, source, "Log for {0} on {1}: {2}".format(source, strLogDate, shortUrl))


logCommand = LogCommand()

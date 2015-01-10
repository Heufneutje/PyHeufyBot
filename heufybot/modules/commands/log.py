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
        self.help = "Commands: log | Provides a link to the source code of the bot."

    def execute(self, server, source, command, params, data):
        if "channel" not in data:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I don't keep logs for private messages.")
            return

        basePath = self.bot.config.serverItemWithDefault(server, "logpath", "logs")
        error = "The date specified is invalid. Make sure you use -<numberofdays> or <yyyy-mm-dd>."
        network = self.bot.servers[server].supportHelper.network

        if len(params) < 1:
            logDate = date.today()
        elif params[0].startswith("-"):
            try:
                delta = int(params[0][1:])
            except ValueError:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, error)
                return
            logDate = date.today() - timedelta(delta)
        else:
            try:
                formattedDate = params[0].split("-")
                logDate = date(int(formattedDate[0]), int(formattedDate[1]), int(formattedDate[2]))
            except (IndexError, ValueError):
               self.bot.servers[server].outputHandler.cmdPRIVMSG(source, error)
               return

        logPath = os.path.join(basePath, network, source, "{}.log".format(logDate.strftime("%Y-%m-%d")))
        if not os.path.exists(logPath):
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I don't have that log.")
            return

        url = "Log for {0} on {1}: http://heufneutje.net/logs/?channel={0}&network={2}&date={1}".format(source[1:],
              logDate.strftime("%Y-%m-%d"), network)

        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, url)

logCommand = LogCommand()

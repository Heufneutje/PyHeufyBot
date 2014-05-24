import os
from datetime import datetime, timedelta
from pyheufybot.moduleinterface import Module, ModuleAccessLevel, ModulePriority, ModuleType
from pyheufybot.utils.fileutils import readFile
from pyheufybot.utils.webutils import pasteEE
from pyheufybot.utils.stringutils import isNumber

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Log"
        self.trigger = "log"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ANYONE
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: log (-<numberofdays>/<date>) | Posts the log for today or a given date to Paste.ee."

    def execute(self, message):
        if len(message.params) == 1:
            logDate = datetime.today().strftime("%Y-%m-%d")
        elif message.params[1].startswith("-"):
            if isNumber(message.params[1][1:]):
                tempDate = datetime.today() - timedelta(days=int(message.params[1][1:]))
                logDate = tempDate.strftime("%Y-%m-%d")
            else:
                self.bot.msg(message.replyTo, "Invalid format. Usage: log (-<numberofdays>/<date>)")
                return True
        else:
            try:
                tempDate = datetime.strptime(message.params[1], "%Y-%m-%d")
                logDate = tempDate.strftime("%Y-%m-%d")
            except ValueError:
                self.bot.msg(message.replyTo, "Invalid format. Usage: log (-<numberofdays>/<date>)")
                return True

        rootLogPath = self.bot.factory.config.getSettingWithDefault("logPath", "logs")
        network = self.bot.serverInfo.network
        logPath = os.path.join(rootLogPath, network, message.channel.name, "{}.log".format(logDate))

        if os.path.exists(logPath):
            logString = readFile(logPath)
            logURL = pasteEE(logString, "Log for {}/{} on {}".format(network, message.channel.name, logDate), 10)
            self.bot.msg(message.replyTo, logURL)
        else:
            self.bot.msg(message.replyTo, "I don't have that log.")

        return True

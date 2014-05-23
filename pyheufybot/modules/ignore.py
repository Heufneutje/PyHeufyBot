import os
from pyheufybot.module_interface import Module, ModulePriority, ModuleType
from pyheufybot.utils import fileutils

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "Ignore"
        self.trigger = "ignore|unignore"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.ABOVENORMAL
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: ignore (<user>), unignore <user>  | Adds the given user to the bot's ignore list. The format is nick!user@host."

        self.ignorePath = os.path.join("data", self.bot.factory.config.getSettingWithDefault("server", "irc.foo.bar"), "ignores.txt")
        self.ignoreList = []

    def execute(self, message):
        print self.ignorePath
        print self.ignoreList
        if message.params[0].lower() == "ignore":
            if len(message.params) == 1:
                if len(self.ignoreList) > 0:
                    self.bot.msg(message.replyTo, "Currently ignoring users: {}.".format(", ".join(self.ignoreList)))
                else:
                    self.bot.msg(message.replyTo, "Currently not ignoring any users.")
            else:
                ignore = " ".join(message.params[1:]).lower()
                if ignore not in self.ignoreList:
                    self.ignoreList.append(ignore)
                    self.writeData()
                    self.bot.msg(message.replyTo, "\"{}\" was added to the ignore list.".format(ignore))
                else:
                    self.bot.msg(message.replyTo, "\"{}\" is already on the ignore list.")
        return True

    def onModuleLoaded(self):
        self.loadData()

    def onModuleUnloaded(self):
        self.writeData()

    def reloadData(self):
        self.loadData()

    def loadData(self):
        if os.path.exists(self.ignorePath):
            self.ignoreList = fileutils.readFile(self.ignorePath).split("\n")

    def writeData(self):
        for ignore in self.ignoreList:
            fileutils.writeFile(self.ignorePath, "{}\n".format(ignore))

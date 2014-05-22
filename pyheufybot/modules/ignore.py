import os
from pyheufybot.module_interface import Module, ModulePriority, ModuleType
from pyheufybot.utils import fileutils

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "Ignore"
        self.trigger = "ignore"
        self.moduleType = ModuleType.COMMAND
        self.modulePriotity = ModulePriority.ABOVENORMAL
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: ignore (<user>), unignore <user>  | Adds the given user to the bot's ignore list. The format is nick!user@host."

        self.ignorePath = os.path.join("data", self.bot.factory.config.getSettingWithDefault("server", "irc.foo.bar"), "ignores.txt")
        self.ignoreList = []

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "Say what?")
        else:
            self.bot.msg(message.replyTo, " ".join(message.params[1:]))
        return True

    def onModuleLoaded(self):
        self.loadData()

    def onModuleUnloaded(self):
        pass

    def loadData(self):
        if os.path.exists(self.ignorePath):
            pass

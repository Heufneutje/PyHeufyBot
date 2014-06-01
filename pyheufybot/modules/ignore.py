import json, os
from pyheufybot.modulehandler import Module, ModuleAccessLevel, ModulePriority, ModuleType
from pyheufybot.utils.fileutils import readFile, writeFile

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Ignore"
        self.trigger = "ignore|unignore"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ADMINS
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: ignore (<user>), unignore <user>  | Adds the given user to the bot's ignore list. The format is nick!user@host."

        self.ignorePath = os.path.join(bot.moduleHandler.dataPath, "ignores.json")
        self.ignoreList = []

    def execute(self, message):
        if message.params[0].lower() == "ignore":
            if len(message.params) == 1:
                if len(self.ignoreList) > 0:
                    self.bot.msg(message.replyTo, "Currently ignoring users: {}.".format(", ".join(self.ignoreList)))
                else:
                    self.bot.msg(message.replyTo, "Currently not ignoring any users.")
            else:
                ignore = " ".join(message.params[1:]).lower()
                if ignore in self.ignoreList:
                    self.bot.msg(message.replyTo, "\"{}\" is already on the ignore list!".format(ignore))
                else:
                    self.ignoreList.append(ignore)
                    self.writeData()
                    self.bot.msg(message.replyTo, "\"{}\" was added to the ignore list.".format(ignore))
        elif message.params[0].lower() == "unignore":
            if len(message.params) == 1:
                self.bot.msg(message.replyTo, "Who do you want me to unignore?")
            else:
                ignore = " ".join(message.params[1:]).lower()
                if ignore in self.ignoreList:
                    self.ignoreList.remove(ignore)
                    self.writeData()
                    self.bot.msg(message.replyTo, "\"{}\" was removed from the ignore list.".format(ignore))
                else:
                    self.bot.msg(message.replyTo, "\"{}\" is not on the ignore list!".format(ignore))
        return True

    def onModuleLoaded(self):
        self.loadData()

    def onModuleUnloaded(self):
        self.writeData()

    def reloadData(self):
        self.loadData()

    def loadData(self):
        if os.path.exists(self.ignorePath):
            try:
                jsonString = readFile(self.ignorePath)
                self.ignoreList = json.loads(jsonString)
            except ValueError:
                # String read is not JSON, use default instead
                pass

    def writeData(self):
        jsonString = json.dumps(self.ignoreList)
        writeFile(self.ignorePath, jsonString)
        self.bot.moduleHandler.reloadModuleData(["ignoreauto"])

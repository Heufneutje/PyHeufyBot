import json, os, re
from pyheufybot.modulehandler import Module, ModulePriority, ModuleType
from pyheufybot.utils.fileutils import readFile

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "IgnoreAuto"
        self.moduleType = ModuleType.PASSIVE
        self.modulePriority = ModulePriority.ABOVENORMAL
        self.messageTypes = ["PRIVMSG", "ACTION"]
        self.helpText = "Prevents users that are on the ignore list from executing any commands or triggers."

        self.ignorePath = os.path.join(bot.moduleInterface.dataPath, "ignores.json")
        self.ignoreList = []

    def execute(self, message):
        for ignore in self.ignoreList:
            match = re.search(ignore, message.user.getFullName(), re.IGNORECASE)
            if match:
                return False

        return True

    def onModuleLoaded(self):
        self.loadData()
        print self.ignoreList

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

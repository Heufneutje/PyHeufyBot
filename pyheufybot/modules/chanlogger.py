from pyheufybot.module_interface import Module, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "ChanLogger"
        self.moduleType = ModuleType.PASSIVE
        self.modulePriority = ModulePriority.HIGH
        self.messageTypes = ["PRIVMSG", "ACTION", "NOTICE", "JOIN", "PART", "NICK", "QUIT", "KICK", "MODE", "TOPIC"]
        self.helpText = "Logs all IRC events to file."

        self.logPath = None

    def execute(self, message):
        return True

    def onModuleLoaded(self):
        self.logPath = config.getSettingWithDefault("logPath", "logs")

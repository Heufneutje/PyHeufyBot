from pyheufybot.module_interface import Module, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "Help"
        self.trigger = "help|modules"
        self.moduleType = ModuleType.COMMAND
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: help/modules (<module/command>) | Makes the bot say the given line"

    def execute(self, message):
        if len(message.params) == 1:
            includePassive = False if message.params[0] == "help" else True
            helpPrefix = "Loaded command/trigger modules: " if message.params[0] == "help" else "Loaded modules:"
            loadedModules = []

            for module in self.bot.moduleInterface.modules.values():
                if module.moduleType != ModuleType.PASSIVE or (module.moduleType == ModuleType.PASSIVE and includePassive):
                    loadedModules.append(module.name)

            self.bot.msg(message.replyTo, "{} {}".format(helpPrefix, ", ".join(loadedModules)))
        else:
            pass

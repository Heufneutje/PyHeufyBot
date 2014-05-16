import re
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
            includePassive = False if message.params[0].lower() == "help" else True
            helpPrefix = "Loaded command/trigger modules: " if message.params[0] .lower() == "help" else "Loaded modules:"
            loadedModules = []

            for module in self.bot.moduleInterface.modules.values():
                if module.moduleType != ModuleType.PASSIVE or (module.moduleType == ModuleType.PASSIVE and includePassive):
                    loadedModules.append(module.name)

            self.bot.msg(message.replyTo, "{} {}".format(helpPrefix, ", ".join(loadedModules)))
        elif message.params[0].lower() == "help":
            helpMessage = " ".join(message.params[1:]).lower()
            for module in self.bot.moduleInterface.modules.values():
                match = re.search(module.trigger.lower(), helpMessage.lower(), re.IGNORECASE)
                if helpMessage.lower() == module.name.lower() or match:
                    self.bot.msg(message.replyTo, module.getHelp(helpMessage))
                    return
            self.bot.msg(message.replyTo, "Module or command \"{}\" was not found.".format(helpMessage))

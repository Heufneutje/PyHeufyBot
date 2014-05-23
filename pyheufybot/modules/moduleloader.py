from pyheufybot.moduleinterface import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "ModuleLoader"
        self.trigger = "load|unload|reload"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ADMINS
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: load/unload/reload <module> | Loads, unloads or reloads a bot module."

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "You didn't specify a parameter! Usage: load/unload/reload <module>.")
            return True
        
        success = []
        failure = []
        result = []

        for module in message.params[1:]:
            if message.params[0].lower() == "load":
                result = self.bot.moduleInterface.loadModule(module)
            elif message.params[0].lower() == "unload":
                result = self.bot.moduleInterface.unloadModule(module)
            elif message.params[0].lower() == "reload":
                result = self.bot.moduleInterface.reloadModule(module)

            if result[0]:
                success.append(result[1])
            else:
                failure.append(result[1][:len(result[1]) - 1])

        if len(success) > 0:
            plural = "s" if len(success) > 1 else ""
            waswere = "were" if len(success) > 1 else "was"
            command = message.params[0][:2] if len(message.params[0]) > 4 else ""

            self.bot.msg(message.replyTo, "Module{} \"{}\" {} successfully {}loaded!".format(plural, "\", \"".join(success), waswere, command))

        if len(failure) > 0:
            self.bot.msg(message.replyTo, "{}.".format(", ".join(failure)))
        return True

    def getHelp(self, command):
        if command == "load":
            return "Usage: load <module> | Loads a bot module."
        elif command == "unload":
            return "Usage: unload <module> | Unloads a loaded bot module."
        elif command == "reload":
            return "Usage: reload <module> | Reloads a loaded bot module."
        else:
            return self.helpText

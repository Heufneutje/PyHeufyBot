from pyheufybot.module_interface import Module, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "ModuleLoader"
        self.trigger = "load|unload|reload"
        self.moduleType = ModuleType.COMMAND
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "No help yet"

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "You didn't specify a parameter! Usage: load/unload/reload <module>")
            return
        
        success = []
        failure = []
        result = []

        for module in message.params[1:]:
            if message.params[0] == "load":
                result = self.bot.moduleInterface.loadModule(module)
            elif message.params[0] == "unload":
                result = self.bot.moduleInterface.unloadModule(module)
            elif message.params[0] == "reload":
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

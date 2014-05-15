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

        if message.params[0] == "load":
           for module in message.params[1:]:
               result = self.bot.moduleInterface.loadModule(module)
               if result[0]:
                   success.append(result[1])
               else:
                   failure.append(result[1][:len(result[1]) - 1])

           if len(success) > 0:
               self.bot.msg(message.replyTo, "Module{} \"{}\" {} successfully loaded!".format("s" if len(success) > 1 else "", "\", \"".join(success), "were" if len(success) > 1 else "was"))

           if len(failure) > 0:
               self.bot.msg(message.replyTo, "{}.".format(", ".join(failure)))

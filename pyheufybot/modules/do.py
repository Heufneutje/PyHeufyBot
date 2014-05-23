from pyheufybot.moduleinterface import Module, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Do"
        self.trigger = "do"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: do <message> | Makes the bot perform the given action."

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "Do what?")
        else:
            self.bot.describe(message.replyTo, " ".join(message.params[1:]))
        return True

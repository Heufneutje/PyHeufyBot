from pyheufybot.moduleinterface import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Source"
        self.trigger = "source"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ANYONE
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: source | Gives a link to the bot's source code on GitHub."

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "https://github.com/Heufneutje/PyHeufyBot")
        return True

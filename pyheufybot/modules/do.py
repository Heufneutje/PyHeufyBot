from pyheufybot.modulehandler import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Do"
        self.trigger = "do|doremote"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ANYONE
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: do <message>/doremote <target> <message>  | Makes the bot perform the given line."

    def execute(self, message):
        if message.params[0].lower() == "do":
            if len(message.params) == 1:
                self.bot.msg(message.replyTo, "Do what?")
            else:
                self.bot.describe(message.replyTo, " ".join(message.params[1:]))
        elif message.params[0].lower() == "doremote":
            if len(message.params) < 3:
                self.bot.msg(message.replyTo, "Do what?")
            else:
                self.bot.describe(message.params[1], " ".join(message.params[2:]))
        return True

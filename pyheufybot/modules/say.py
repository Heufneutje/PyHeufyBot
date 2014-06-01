from pyheufybot.modulehandler import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Say"
        self.trigger = "say|sayremote"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ANYONE
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: say <message>/sayremote <target> <message>  | Makes the bot say the given line."

    def execute(self, message):
        if message.params[0].lower() == "say":
            if len(message.params) == 1:
                self.bot.msg(message.replyTo, "Say what?")
            else:
                self.bot.msg(message.replyTo, " ".join(message.params[1:]))
        elif message.params[0].lower() == "sayremote":
            if len(message.params) < 3:
                self.bot.msg(message.replyTo, "Say what?")
            else:
                self.bot.msg(message.params[1], " ".join(message.params[2:]))
        return True

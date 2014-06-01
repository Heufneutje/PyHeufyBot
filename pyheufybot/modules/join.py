from pyheufybot.modulehandler import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Join"
        self.trigger = "join"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ANYONE
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: join <channel> | Makes the bot join the given channel."

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "Join what?")
        else:
            chanName = message.params[1].lower()
            if chanName[0] not in self.bot.serverInfo.chanTypes:
                chanName = "#{}".format(chanName)
            if chanName in self.bot.channels:
                self.bot.msg(message.replyTo, "I'm already in that channel!")
            else:
                self.bot.join(chanName)
        return True

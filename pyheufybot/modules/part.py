from pyheufybot.moduleinterface import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Part"
        self.trigger = "part"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ADMINS
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: part <channel> (<message>) | Makes the bot leave the given channel."

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "Part what?")
        else:
            chanName = message.params[1].lower()
            if chanName[0] not in self.bot.serverInfo.chanTypes:
                chanName = "#{}".format(chanName)
            if chanName not in self.bot.channels:
                self.bot.msg(message.replyTo, "I'm not in that channel!")
            else:
                if len(message.params) > 2:
                    self.bot.leave(chanName, " ".join(message.params[2:]))
                else:
                    self.bot.leave(chanName)
        return True

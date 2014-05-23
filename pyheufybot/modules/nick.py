import re
from pyheufybot.moduleinterface import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Nick"
        self.trigger = "nick"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ANYONE
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: nick <message> | Changes the bot's nickname."

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "Change my nick to what?")
        else:
            nickname = " ".join(message.params[1:])
            match = re.search(r"[a-zA-Z\[\]\\`_^{}\|][a-zA-Z0-9-\[\]\\`_^{}\|]$", nickname)
            if match and len(nickname) <= self.bot.serverInfo.nicklength:
                self.bot.setNick(nickname)
            else:
                self.bot.msg(message.replyTo, "That is not a valid nickname.")
        return True

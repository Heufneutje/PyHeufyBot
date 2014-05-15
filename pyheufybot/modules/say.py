from pyheufybot.module_interface import Module, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "Say"
        self.trigger = "say"
        self.moduleType = ModuleType.COMMAND
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: say <message> | Makes the bot say the given line"

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "Say what?")
        else:
            self.bot.msg(message.replyTo, " ".join(message.params[1:]))

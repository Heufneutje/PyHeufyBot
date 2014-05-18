from pyheufybot.module_interface import Module, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "Source"
        self.trigger = "source"
        self.moduleType = ModuleType.COMMAND
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: source | Gives a link to the bot's source code on GitHub."

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "https://github.com/Heufneutje/PyHeufyBot")

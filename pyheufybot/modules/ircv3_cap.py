from pyheufybot.module_interface import Module, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "IRCv3_CAP"
        self.moduleType = ModuleType.PASSIVE
        self.messageTypes = ["CONNECT"]
        self.helpText = "Enables the client capability negotiation mechanism. (See http://ircv3.org/)"

    def execute(self, message):
        if message.messageType == "CONNECT":
            self.bot.sendLine("CAP LS")

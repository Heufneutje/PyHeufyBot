from pyheufybot.module_interface import Module, ModuleType
from pyheufybot.message import IRCResponse, ResponseType

class ModuleSpawner(Module):
    def __init__(self):
        self.name = "Say"
        self.trigger = "say"
        self.moduleType = ModuleType.ACTIVE
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: say <message> | Makes the bot say the given line"

    def execute(self, message):
        return [ IRCResponse(message.replyTo, message.messageText, ResponseType.MESSAGE) ]

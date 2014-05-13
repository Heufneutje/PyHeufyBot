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
        if len(message.params) == 1:
            return [ IRCResponse(message.replyTo, "Say what?", ResponseType.MESSAGE) ]
        else:
            return [ IRCResponse(message.replyTo, " ".join(message.params[1:]), ResponseType.MESSAGE) ]

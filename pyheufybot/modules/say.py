from module_interface import Module, ModuleType

class Say(Module):
    def __init__(self):
        self.trigger = "say"
        self.moduleType = ModuleType.ACTIVE
        self.messagesTypes = ["PRIVMSG"]
        self.helpText = "Usage: say <message> | Makes the bot say the given line"

    def execute(self, message, serverInfo):
        pass

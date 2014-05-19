from pyheufybot.module_interface import Module, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "IRCv3_multi-prefix"
        self.moduleType = ModuleType.PASSIVE
        self.messageTypes = ["CAP LS", "CAP ACK", "CAP NAK"]
        self.helpText = "Enables the multi-prefix capability."

    def execute(self, message):
        if message.messageType == "CAP LS":
            if self.name[6:] in self.bot.capHandler.availableCaps:
                self.bot.sendLine("CAP REQ :{}".format(self.name[6:]))
        elif message.messageType == "CAP ACK":
            print message.params
            self.bot.capHandler.finishedCaps.append(name[6:])

    def onModuleLoad(self):
        if self.name[6:] not in self.bot.capHandler.enabledCaps:
            self.bot.capHandler.enabledCaps.append(self.name[6:])

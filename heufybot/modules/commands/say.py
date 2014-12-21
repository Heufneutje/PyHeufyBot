from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class SayCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Say"

    def triggers(self):
        return ["say", "sayto"]

    def execute(self, server, source, command, params, data):
        if command == "say" and len(params) < 1 or command == "sayto" and len(params) < 2:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Say what?")
            return
        if command == "say":
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, " ".join(params))
        elif command == "sayto":
            self.bot.servers[server].outputHandler.cmdPRIVMSG(params[0], " ".join(params[1:]))

sayCommand = SayCommand()

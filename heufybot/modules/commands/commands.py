from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class CommandsCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Commands"

    def triggers(self):
        return ["commands"]

    def load(self):
        self.help = "Commands: commands | Lists all bot commands from the modules that are enabled for this server."
        self.commandHelp = {}

    def execute(self, server, source, command, params, data):
        commandsList = []
        for moduleName, module in self.bot.moduleHandler.loadedModules.iteritems():
            if self.bot.moduleHandler.useModuleOnServer(moduleName, server) and isinstance(module, BotCommand):
                commandsList += module.triggers()
        self.replyPRIVMSG(server, source, "Available commands: {}".format(", ".join(sorted(commandsList))))


commandsCommand = CommandsCommand()

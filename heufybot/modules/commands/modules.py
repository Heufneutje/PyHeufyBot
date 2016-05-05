from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class ModulesCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Modules"

    def triggers(self):
        return ["modules"]

    def load(self):
        self.help = "Commands: modules | Show a list of all loaded modules."
        self.commandHelp = {}

    def execute(self, server, source, command, params, data):
        loadedModules = sorted(self.bot.moduleHandler.loadedModules.keys())
        self.replyNOTICE(server, source, "Loaded modules: {}".format(", ".join(loadedModules)))


modulesCommand = ModulesCommand()

from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class HelpCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Help"

    def triggers(self):
        return ["help"]

    def load(self):
        self.help = "Commands: help (<command/trigger>) | Displays help for a given command module or command trigger " \
                    "or show a list of all enabled command modules."
        self.commandHelp = {}

    def execute(self, server, source, command, params, data):
        if len(params) < 1:
            commandModules = []
            for module in self.bot.moduleHandler.enabledModules[server]:
                if isinstance(self.bot.moduleHandler.loadedModules[module], BotCommand):
                    commandModules.append(module)
            message = "Loaded command modules: {}".format(", ".join(sorted(commandModules)))
            self.replyPRIVMSG(server, source, message)
        else:
            helpText = self.bot.moduleHandler.runActionUntilValue("commandhelp", server, params[0])
            if helpText:
                self.replyPRIVMSG(server, source, helpText)
            else:
                error = "No command modules or command triggers named \"{}\" were found.".format(params[0])
                self.replyPRIVMSG(server, source, error)


helpCommand = HelpCommand()

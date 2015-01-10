from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class SourceCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Source"

    def triggers(self):
        return ["source"]

    def load(self):
        self.help = "Commands: source | Provides a link to the source code of the bot."

    def execute(self, server, source, command, params, data):
        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "https://github.com/Heufneutje/PyHeufyBot")

sourceCommand = SourceCommand()

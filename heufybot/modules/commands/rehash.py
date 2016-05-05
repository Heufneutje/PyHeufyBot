from twisted.plugin import IPlugin
from heufybot.config import ConfigError
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class RehashCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Rehash"

    def triggers(self):
        return ["rehash"]

    def load(self):
        self.help = "Commands: rehash | Rehashes the bot's configuration files."
        self.commandHelp = {}

    def checkPermissions(self, server, source, user, command):
        return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user, "rehash")

    def execute(self, server, source, command, params, data):
        try:
            self.bot.config.loadConfig()
            self.replyPRIVMSG(server, source, "Rehashed the configuration successfully.")
        except ConfigError as e:
            self.replyPRIVMSG(server, source, e)


rehashCommand = RehashCommand()

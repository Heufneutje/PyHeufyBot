from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class NickCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Nick"

    def triggers(self):
        return ["nick"]

    def load(self):
        self.help = "Commands: nick | Change the nickname of the bot."
        self.commandHelp = {}

    def checkPermissions(self, server, source, user, command):
        return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                              "connection-control")

    def execute(self, server, source, command, params, data):
        if len(params) < 1:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Change my nick to what?")
        else:
            self.bot.servers[server].outputHandler.cmdNICK(params[0])

nickCommand = NickCommand()

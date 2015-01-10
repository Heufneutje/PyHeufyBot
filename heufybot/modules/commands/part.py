from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class PartCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Part"

    def triggers(self):
        return ["part"]

    def load(self):
        self.help = "Commands: part <channel> | Make the bot leave a given channel. Requires admin permissions."

    def checkPermissions(self, server, source, user, command):
        return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                              "channel-control")

    def execute(self, server, source, command, params, data):
        if len(params) < 1 and "channel" not in data:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Part what?")
        elif len(params) < 1:
            self.bot.servers[server].outputHandler.cmdPART(source, "Leaving...")
        else:
            if params[0] not in self.bot.servers[server].channels:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I am not in {}".format(params[0]))
            elif len(params) == 1:
                self.bot.servers[server].outputHandler.cmdPART(params[0], "Leaving...")
            else:
                self.bot.servers[server].outputHandler.cmdPART(params[0], " ".join(params[1:]))

partCommand = PartCommand()

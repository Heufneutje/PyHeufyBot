from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class JoinCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Join"

    def triggers(self):
        return ["join"]

    def load(self):
        self.help = "Commands: join <channel> | Make the bot join a given channel."

    def execute(self, server, source, command, params, data):
        if len(params) < 1:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Join what?")
            return

        if len(params) > 1:
            self.bot.servers[server].outputHandler.cmdJOIN(params[0], params[1])
        else:
            self.bot.servers[server].outputHandler.cmdJOIN(params[0])

joinCommand = JoinCommand()

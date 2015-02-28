from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils.timeutils import now, timeDeltaString
from zope.interface import implements


class UptimeCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Uptime"

    def triggers(self):
        return ["uptime"]

    def load(self):
        self.help = "Commands: uptime | Provides the current uptime of the bot."

    def execute(self, server, source, command, params, data):
        delta = timeDeltaString(now(), self.bot.startTime)
        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I have been up for {}.".format(delta))

uptimeCommand = UptimeCommand()

from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils.timeutils import now, strftimeWithTimezone, timeDeltaString
from zope.interface import implements


class UptimeCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Uptime"

    def triggers(self):
        return ["uptime"]

    def load(self):
        self.help = "Commands: uptime | Provides the current uptime of the bot."
        self.commandHelp = {}

    def execute(self, server, source, command, params, data):
        start = strftimeWithTimezone(self.bot.startTime)
        delta = timeDeltaString(now(), self.bot.startTime)
        self.replyPRIVMSG(server, source, "I have been up since {} ({}).".format(start, delta))


uptimeCommand = UptimeCommand()

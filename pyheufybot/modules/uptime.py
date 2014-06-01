from datetime import datetime
from pyheufybot.utils import stringutils
from pyheufybot.modulehandler import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Uptime"
        self.trigger = "uptime"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ANYONE
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: uptime | Shows you how long the bot has been running."

        self.startTime = None

    def execute(self, message):
        if len(message.params) == 1:
            now = datetime.utcnow()
            delta = now - self.startTime
            formattedDate = self.startTime.strftime("%Y-%m-%d %H:%M:%S UTC")
            formattedDelta = stringutils.strfdelta(delta, "{days} day(s), {hours} hour(s), {minutes} minute(s) and {seconds} second(s)")
            self.bot.msg(message.replyTo, "I have been running since {} ({})".format(formattedDate, formattedDelta))
        return True

    def onModuleLoaded(self):
        self.startTime = datetime.utcnow()

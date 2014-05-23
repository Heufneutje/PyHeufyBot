import os, time
from pyheufybot.module_interface import Module, ModulePriority, ModuleType
from pyheufybot.logger import log
from pyheufybot.utils.fileutils import createDirs, writeFile

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "ChanLogger"
        self.moduleType = ModuleType.PASSIVE
        self.modulePriority = ModulePriority.HIGH
        self.messageTypes = ["PRIVMSG", "ACTION", "NOTICE", "JOIN", "PART", "NICK", "QUIT", "KICK", "MODE", "TOPIC"]
        self.helpText = "Logs all IRC events to file."

        self.logPath = None

    def logFile(self, target, messageText):
        server = self.bot.serverInfo.network
        todayDate = time.strftime("%Y-%m-%d")
        todayTime = time.strftime("%H:%M:%S")

        createDirs(os.path.join(self.logPath, server, target))
        path = os.path.join(self.logPath, server, target, "{}.log".format(todayDate))
        writeFile(path, "[{}] {}\n".format(todayTime, messageText), True)
        log(messageText, "{}/{}".format(server, target))

    def execute(self, message):
        if message.messageType == "PRIVMSG":
            statusChar = ""
            if message.channel and message.channel.ranks[message.user.nickname] != "":
                statusChar = self.bot.serverInfo.prefixesModeToChar[message.channel.getHighestRankOfUser(message.user.nickname, self.bot.serverInfo.prefixOrder)]
            logString = "<{}{}> {}".format(statusChar, message.user.nickname, message.messageText)
            self.logFile(message.replyTo, logString)
        elif message.messageType == "ACTION":
            logString = "* {} {}".format(message.user.nickname, message.messageText)
            self.logFile(message.replyTo, logString)
        elif message.messageType == "NOTICE":
            logString = "[{}] {}".format(message.replyTo, message.messageText)
            self.logFile(message.replyTo, logString)
        elif message.messageType == "JOIN":
            logString = ">> {} ({}@{}) has joined {}".format(message.user.nickname, message.user.username, message.user.hostname, message.channel.name)
            self.logFile(message.replyTo, logString)
        elif message.messageType == "PART":
            logString = "<< {} ({}@{}) has left {} ({})".format(message.user.nickname, message.user.username, message.user.hostname, message.channel.name, message.messageText)
            self.logFile(message.replyTo, logString)
        elif message.messageType == "QUIT":
            logString = "<< {} ({}@{}) has quit IRC ({})".format(message.user.nickname, message.user.username, message.user.hostname, message.messageText)
            for channel in self.bot.channels.values():
                if message.user.nickname in channel.users:
                    self.logFile(channel.name, logString)
        elif message.messageType == "NICK":
            logString = "-- {} is now known as {}".format(message.messageText, message.user.nickname)
            for channel in self.bot.channels.values():
                if message.user.nickname in channel.users:
                    self.logFile(channel.name, logString)
        elif message.messageType == "KICK":
            logString = "<< {} was kicked from {} by {} ({})".format(message.params[0], message.channel.name, message.user.nickname, message.params[1:])
            self.logFile(message.replyTo, logString)
        elif message.messageType == "MODE":
            logString = "## {} set mode: {}".format(message.user.nickname, message.messageText)
            self.logFile(message.replyTo, logString)
        elif message.messageType == "TOPIC":
            logString = "-- {} changes topic to \"{}\"".format(message.user.nickname, message.messageText)
            self.logFile(message.replyTo, logString)
        return True

    def onModuleLoaded(self):
        config = self.bot.factory.config
        self.logPath = config.getSettingWithDefault("logPath", "logs")

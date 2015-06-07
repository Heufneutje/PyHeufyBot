from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements
from os import walk
from time import strftime
import os.path, re


class LogsearchCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "LogSearch"

    def triggers(self):
        return ["firstseen", "lastseen", "lastsaw", "firstsaid", "lastsaid"]

    def load(self):
        self.help = "Commands: firstseen <nick>, lastseen <nick>, lastsaw <nick>, firstsaid <message>, " \
                    "lastsaid <message> | Search the logs by nickname or (part of) a message."
        self.commandHelp = {
            "firstseen": "firstseen <nick> | Search for the first line someone with the given nick spoke.",
            "lastseen": "lastseen <nick> | Search for the last line someone with the given nick spoke. Includes today.",
            "lastsaw": "lastsaw <nick> | Search for the last line someone with the given nick spoke. Does not include "
                       "today.",
            "firstsaid": "firstsaid <nick> | Search for the first time a given thing was said.",
            "lastsaid": "lastsaid <nick> | Search for the last time a given thing was said."
        }

    def execute(self, server, source, command, params, data):
        if len(params) < 1:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Search what?")
            return

        basePath = self.bot.config.serverItemWithDefault(server, "logpath", "logs")
        if self.bot.servers[server].supportHelper.network:
            network = self.bot.servers[server].supportHelper.network
        else:
            network = server
        logPath = os.path.join(basePath, network, source)
        logs = []
        for (dirpath, dirnames, filenames) in walk(logPath):
            logs.extend(filenames)
            break

        result = None
        if command == "firstseen":
            result = self._search(params[0], logPath, logs, True, True, False)
        elif command == "lastseen":
            result = self._search(params[0], logPath, logs, True, True, True)
        elif command == "lastsaw":
            result = self._search(params[0], logPath, logs, True, False, True)
        elif command == "firstsaid":
            result = self._search(params[0], logPath, logs, False, True, False)
        elif command == "lastsaid":
            result = self._search(params[0], logPath, logs, False, True, True)

        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, result)

    def _search(self, searchTerms, logPath, files, searchForNick, includeToday, reverse):
        if searchForNick:
            pattern = re.compile(r".*<(.?{})> .*".format(searchTerms), re.IGNORECASE)
        else:
            pattern = re.compile(r".*<.*> .*({}).*".format(searchTerms), re.IGNORECASE)
        found = None

        if not includeToday:
            today = "{}.log".format(strftime("%Y-%m-%d"))
            if today in files:
                files.remove(today)

        if reverse:
            files.reverse()
        for filename in files:
            with open(os.path.join(logPath, filename), "r") as logfile:
                if reverse:
                    lines = reversed(logfile.readlines())
                else:
                    lines = logfile.readlines()
            if reverse and includeToday and not searchForNick:
                lines = list(lines)[5:]
            for line in lines:
                if pattern.match(line.rstrip()):
                    found = line.rstrip()
                    break
            if found:
                return "[{}] {}".format(filename[:10], found)
        return "Nothing that matches your search terms has been found in the log."

logsearch = LogsearchCommand()

from twisted.plugin import IPlugin
from heufybot.channel import IRCChannel
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import isNumber
from zope.interface import implements
from weakref import WeakKeyDictionary
import random, re, time


class OutOfContextCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "OutOfContext"

    def triggers(self):
        return ["ooc"]

    def actions(self):
        return super(OutOfContextCommand, self).actions() + [
            ("ctcp-message", 1, self.bufferAction),
            ("message-channel", 1, self.bufferMessage) ]

    def load(self):
        self.help = "Nope."
        if "ooclog" not in self.bot.storage:
            self.bot.storage["ooclog"] = {}
        self.ooclog = self.bot.storage["ooclog"]
        self.messageBuffer = WeakKeyDictionary()
        self.historySize = 20

    def execute(self, server, source, command, params, data):
        if server not in self.ooclog:
            self.ooclog[server] = {}
        if source not in self.ooclog[server]:
            self.ooclog[server][source] = []
        if len(params) == 0:
            params.append("list")
        subcommand = params.pop(0).lower()
        if subcommand not in ["add", "remove", "search", "searchnick", "random", "id", "list"]:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Invalid subcommand. Subcommands are "
                                                                      "add/remove/search/searchnick/random/id/list.")
            return
        if subcommand == "add":
            if len(params) == 0:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Add what?")
                return
            if "channel" not in data:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "You can only add quotes from a channel.")
                return
            regex = re.compile(" ".join(params), re.IGNORECASE)
            matches = filter(regex.search, self.messageBuffer[self.bot.servers[server]][data["channel"]])
            if len(matches) == 0:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Sorry, that didn't match anything in my "
                                                                          "message buffer.")
            elif len(matches) > 1:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Sorry, that matches too many lines in my "
                                                                          "message buffer.")
            else:
                todayDate = time.strftime("[%Y-%m-%d %H:%M]")
                quote = "{} {}".format(todayDate, matches[0])
                if quote.lower() in [x.lower() for x in self.ooclog[server][source]]:
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "That quote is already in the log!")
                else:
                    self.ooclog[server][source].append(quote)
                    self.bot.storage["ooclog"] = self.ooclog
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Quote \"{}\" was added the "
                                                                              "log!".format(quote))
        elif subcommand == "remove":
            if len(params) == 0:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Remove what?")
                return
            regex = re.compile(" ".join(params), re.IGNORECASE)
            matches = filter(regex.search, self.ooclog[server][source])
            if len(matches) == 0:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "That quote is not in the log.")
            elif len(matches) > 1:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Unable to remove quote, {} matches "
                                                                          "found.".format(len(matches)))
            else:
                self.ooclog[server][source].remove(matches[0])
                self.bot.storage["ooclog"] = self.ooclog
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Quote \"{}\" was removed from "
                                                                          "log!".format(matches[0]))
        elif subcommand == "random":
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, self._getQuote(server, source, "", False, -1))
        elif subcommand == "searchnick" or subcommand == "search":
            searchNick = subcommand == "searchnick"
            if len(params) == 0:
                quote = self._getQuote(server, source, data["user"].nick, searchNick, -1)
            elif len(params) == 1:
                quote = self._getQuote(server, source, params[0], searchNick, -1)
            elif isNumber(params[len(params) - 1]):
                quote = self._getQuote(server, source, " ".join(params[:len(params) - 1]), searchNick,
                                       int(params[len(params) - 1]) - 1)
            else:
                quote = self._getQuote(server, source, " ".join(params), searchNick, -1)
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, quote)
        elif subcommand == "id":
            if len(params) == 0 or not isNumber(params[0]):
                quote = "You didn't specify a valid ID."
            else:
                quote = self._getQuote(server, source, "", False, int(params[0]) - 1)
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, quote)
        elif subcommand == "list":
            if len(params) > 0:
                subsubcommand = params.pop(0).lower()
                if subsubcommand == "searchnick":
                    result = self._postList(server, source, " ".join(params), True)
                elif subsubcommand == "search":
                    result = self._postList(server, source, " ".join(params), False)
                else:
                    result = self._postList(server, source, "", False)
            else:
                result = self._postList(server, source, "", False)
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, result)

    def _getQuote(self, server, source, searchString, searchNickname, index):
        if len(self.ooclog[server][source]) == 0:
            return "No quotes in the log."
        regex = re.compile(searchString, re.IGNORECASE)
        matches = []
        if searchNickname:
            for x in self.ooclog[server][source]:
                if re.search(regex, x[x.find("<") + 1:x.find(">")]) or re.search(regex, x[:x.find(" ", beg=21)]):
                    matches.append(x)
        else:
            for x in self.ooclog[server][source]:
                if re.search(regex, x[x.find(">") + 1:]):
                    matches.append(x)
        if len(matches) == 0:
            return "No matches for \"{}\" found.".format(searchString)
        if index < 0 or index > len(matches) - 1:
            index = random.randint(0, len(matches) - 1)
        return "Quote #{}/{}: {}".format(index + 1, len(matches), matches[index])

    def _postList(self, server, source, searchString, searchNickname):
        if len(self.ooclog[server][source]) == 0:
            return "No quotes in the log."
        regex = re.compile(searchString, re.IGNORECASE)
        matches = []
        if searchNickname:
            for x in self.ooclog[server][source]:
                if re.search(regex, x[x.find("<") + 1:x.find(">")]) or re.search(regex, x[:x.find(" ", beg=21)]):
                    matches.append(x)
        else:
            for x in self.ooclog[server][source]:
                if re.search(regex, x[x.find(">") + 1:]):
                    matches.append(x)
        if len(matches) == 0:
            return "No matches for \"{}\" found.".format(searchString)
        result = self.bot.moduleHandler.runActionUntilValue("post-paste", "OoC Log", "\n".join(matches), 10)
        if not result:
            return "An error occurred. The PasteEE API seems to be down right now."
        return "List posted: {}".format(result)

    def bufferAction(self, server, source, user, body):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return
        if not isinstance(source, IRCChannel):
            return
        if not body.upper().startswith("ACTION"):
            return
        self._bufferLine(self.bot.servers[server], source, "* {} {}".format(user.nick, body[7:]))

    def bufferMessage(self, server, channel, user, body):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return
        self._bufferLine(self.bot.servers[server], channel, "<{}> {}".format(user.nick, body))

    def _bufferLine(self, server, source, line):
        if server not in self.messageBuffer:
            self.messageBuffer[server] = WeakKeyDictionary()
        if source not in self.messageBuffer[server]:
            self.messageBuffer[server][source] = []
        self.messageBuffer[server][source].append(line)
        self.messageBuffer[server][source] = self.messageBuffer[server][source][-self.historySize:]

ooc = OutOfContextCommand()

from twisted.plugin import IPlugin
from heufybot.channel import IRCChannel
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import isNumber, networkName
from zope.interface import implements
from weakref import WeakKeyDictionary
import random, re, time


class OutOfContextCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "OutOfContext"

    def triggers(self):
        return ["oocadd", "oocid", "ooclist", "oocrandom", "oocremove", "oocremoveid", "oocsearch", "oocsearchnick"]

    def actions(self):
        return super(OutOfContextCommand, self).actions() + [
            ("ctcp-message", 1, self.bufferAction),
            ("message-channel", 1, self.bufferMessage) ]

    def load(self):
        self.historySize = 30
        self.help = "Commands: oocadd <quote>, oocid <quoteid>, ooclist (<search/searchnick <regex>), oocrandom, " \
                    "oocremove <regex>, oocremoveid <quoteid>, search <regex>, searchnick <regex>"
        self.commandHelp = {
            "oocadd": "oocadd <quote> | Add a new quote to the OutOfContext log. The quote will be pulled from a {} "
                      "line message buffer".format(self.historySize),
            "oocid": "oocid <quoteid> | Look up the quote that has the given ID",
            "ooclist": "ooclist (<search/searchnick <regex>>) | Post the OutOfContext log to Paste.EE. A search regex "
                       "can be provided to filter the list.",
            "oocrandom": "oocrandom | Return a random quote from the OutOfContext log",
            "oocremove": "oocremove <regex> | Remove a quote from the OutOfContext log.",
            "oocremoveid": "oocremoveid <quoteid> | Remove the quote with the specified ID from the OutOfContext log.",
            "oocsearch": "search <regex> | Look up quotes in the OutOfContext log. This search operation will look at "
                         "the content of the quotes.",
            "oocsearchnick": "searchnick <regex> | Look up quotes in the OutOfContext log. This search operation will "
                             "look at the nick that said the quoted line."
        }
        if "ooclog" not in self.bot.storage:
            self.bot.storage["ooclog"] = {}
        self.ooclog = self.bot.storage["ooclog"]
        self.messageBuffer = WeakKeyDictionary()

    def checkPermissions(self, server, source, user, command):
        if command == "oocremove" or command == "oocremoveid":
            return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                                  "remove-quote")
        return True

    def execute(self, server, source, command, params, data):
        if networkName(self.bot, server) not in self.ooclog:
            self.ooclog[networkName(self.bot, server)] = {}
        if source not in self.ooclog[networkName(self.bot, server)]:
            self.ooclog[networkName(self.bot, server)][source] = []

        if command == "oocadd":
            if len(params) == 0:
                self.replyPRIVMSG(server, source, "Add what?")
                return
            if "channel" not in data:
                self.replyPRIVMSG(server, source, "You can only add quotes from a channel.")
                return
            regex = re.compile(re.escape(" ".join(params)), re.IGNORECASE)
            if len(self.messageBuffer) == 0:
                self.replyPRIVMSG(server, source, "Sorry, there are no lines in my message buffer.")
                return
            matches = filter(regex.search, self.messageBuffer[self.bot.servers[server]][data["channel"]])
            if len(matches) == 0:
                self.replyPRIVMSG(server, source, "Sorry, that didn't match anything in my message buffer.")
            elif len(matches) > 1:
                self.replyPRIVMSG(server, source, "Sorry, that matches too many lines in my message buffer.")
            else:
                todayDate = time.strftime("[%Y-%m-%d] [%H:%M]")
                quote = "{} {}".format(todayDate, matches[0])
                if quote.lower() in [x.lower() for x in self.ooclog[networkName(self.bot, server)][source]]:
                    self.replyPRIVMSG(server, source, "That quote is already in the log!")
                else:
                    self.ooclog[networkName(self.bot, server)][source].append(quote)
                    self.bot.storage["ooclog"] = self.ooclog
                    self.replyPRIVMSG(server, source, "Quote '{}' was added to the log!".format(quote))
        elif command == "oocremove":
            if len(params) == 0:
                self.replyPRIVMSG(server, source, "Remove what?")
                return
            regex = re.compile(" ".join(params), re.IGNORECASE)
            matches = filter(regex.search, self.ooclog[networkName(self.bot, server)][source])
            if len(matches) == 0:
                self.replyPRIVMSG(server, source, "That quote is not in the log.")
            elif len(matches) > 1:
                self.replyPRIVMSG(server, source, "Unable to remove quote, {} matches found.".format(len(matches)))
            else:
                self._removeQuote(server, source, matches[0])
        elif command == "oocremoveid":
            if len(params) == 0 or not isNumber(params[0]):
                self.replyPRIVMSG(server, source, "You didn't specify a valid ID.")
            else:
                index = int(params[0]) - 1
                quotes = self.ooclog[networkName(self.bot, server)][source]
                if index < len(quotes):
                    self._removeQuote(server, source, quotes[index])
                else:
                    self.replyPRIVMSG(server, source, "That quote is not in the log.")
        elif command == "oocrandom":
            self.replyPRIVMSG(server, source, self._getQuote(server, source, "", False, -1))
        elif command == "oocsearchnick" or command == "oocsearch":
            searchNick = command == "oocsearchnick"
            if len(params) == 0:
                quote = self._getQuote(server, source, data["user"].nick, searchNick, -1)
            elif len(params) == 1:
                quote = self._getQuote(server, source, params[0], searchNick, -1)
            elif isNumber(params[len(params) - 1]):
                quote = self._getQuote(server, source, " ".join(params[:len(params) - 1]), searchNick,
                                       int(params[len(params) - 1]) - 1)
            else:
                quote = self._getQuote(server, source, " ".join(params), searchNick, -1)
            self.replyPRIVMSG(server, source, quote)
        elif command == "oocid":
            if len(params) == 0 or not isNumber(params[0]):
                quote = "You didn't specify a valid ID."
            else:
                quote = self._getQuote(server, source, "", False, int(params[0]) - 1)
            self.replyPRIVMSG(server, source, quote)
        elif command == "ooclist":
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
            self.replyPRIVMSG(server, source, result)

    def _getQuote(self, server, source, searchString, searchNickname, index):
        if len(self.ooclog[networkName(self.bot, server)][source]) == 0:
            return "No quotes in the log."
        regex = re.compile(searchString, re.IGNORECASE)
        matches = []
        if searchNickname:
            for x in self.ooclog[networkName(self.bot, server)][source]:
                if x[21] == "*":
                    match = re.search(regex, x[:x.find(" ", 23)])
                else:
                    match = re.search(regex, x[x.find("<") + 1:x.find(">")])
                if match:
                    matches.append(x)
        else:
            for x in self.ooclog[networkName(self.bot, server)][source]:
                if re.search(regex, x[x.find(">") + 1:]):
                    matches.append(x)
        if len(matches) == 0:
            return "No matches for {!r} found.".format(searchString)
        if index < 0 or index > len(matches) - 1:
            index = random.randint(0, len(matches) - 1)
        return "Quote #{}/{}: {}".format(index + 1, len(matches), matches[index])

    def _postList(self, server, source, searchString, searchNickname):
        if len(self.ooclog[networkName(self.bot, server)][source]) == 0:
            return "No quotes in the log."
        regex = re.compile(searchString, re.IGNORECASE)
        matches = []
        if searchNickname:
            for x in self.ooclog[networkName(self.bot, server)][source]:
                if x[21] == "*":
                    match = re.search(regex, x[:x.find(" ", 23)])
                else:
                    match = re.search(regex, x[x.find("<") + 1:x.find(">")])
                if match:
                    matches.append(x)
        else:
            for x in self.ooclog[networkName(self.bot, server)][source]:
                if re.search(regex, x[x.find(">") + 1:]):
                    matches.append(x)
        if len(matches) == 0:
            return "No matches for {!r} found.".format(searchString)
        result = self.bot.moduleHandler.runActionUntilValue("post-paste", "OoC Log", "\n".join(matches), 10)
        if not result:
            return "An error occurred. The PasteEE API seems to be down right now."
        return "List posted: {}".format(result)

    def _removeQuote(self, server, source, quote):
        self.ooclog[networkName(self.bot, server)][source].remove(quote)
        self.bot.storage["ooclog"] = self.ooclog
        self.replyPRIVMSG(server, source, "Quote '{}' was removed from the log!".format(quote))

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
        commandPrefix = self.bot.config.serverItemWithDefault(server, "command_prefix", "!")
        if body.startswith(commandPrefix):
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

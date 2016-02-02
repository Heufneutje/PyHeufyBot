from twisted.plugin import IPlugin
from heufybot.channel import IRCChannel
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import networkName
from zope.interface import implements
import operator


class WordCounterCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "WordCounter"
    commandUsed = False

    def triggers(self):
        return ["addwordcount", "remwordcount", "wordcount"]

    def actions(self):
        return super(WordCounterCommand, self).actions() + [
            ("message-channel", 1, self.countMessage),
            ("ctcp-message", 1, self.countAction) ]

    def load(self):
        self.help = "Commands: addwordcount <word>, remwordcount <word>, wordcount <word> | Add or remove a word that" \
                    " should be counted in the channel or request how many times a given word has been said."
        self.commandHelp = {
            "addwordcount": "addwordcount <word> | Add a word to be counted.",
            "remwordcount": "remwordcount <word> | Remove a word that is being counted.",
            "wordcount": "wordcount <word> | Request how many times a given word has been said."
        }
        if "wordcounts" not in self.bot.storage:
            self.bot.storage["wordcounts"] = {}
        self.wordCounters = self.bot.storage["wordcounts"]

    def checkPermissions(self, server, source, user, command):
        if command == "addwordcount" or command == "remwordcount":
            return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                                  "word-counter")
        else:
            return True

    def execute(self, server, source, command, params, data):
        self.commandUsed = True
        if "channel" not in data:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Word counters can only be used in channels.")
            return
        if len(params) < 1:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "You didn't specify a word.")
            return
        network = networkName(self.bot, server)
        if network not in self.wordCounters:
            self.wordCounters[network] = {}
        if source not in self.wordCounters[network]:
            self.wordCounters[network][source] = {}
        word = params[0].lower()
        if command == "addwordcount":
            if word in self.wordCounters[network][source]:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "A counter for \"{}\" already "
                                                                          "exists.".format(word))
            else:
                self.wordCounters[network][source][word] = {}
                self.bot.storage["wordcounts"] = self.wordCounters
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "A counter for \"{}\" has been "
                                                                          "added.".format(word))
        elif command == "remwordcount":
            if word in self.wordCounters[network][source]:
                del self.wordCounters[network][source][word]
                self.bot.storage["wordcounts"] = self.wordCounters
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "The counter for \"{}\" has been "
                                                                          "removed.".format(word))

            else:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "A counter for \"{}\" does not "
                                                                          "exist.".format(word))
        elif command == "wordcount":
            self.commandUsed = True
            if word not in self.wordCounters[network][source]:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "A counter for \"{}\" does not "
                                                                          "exist.".format(word))
                return
            total = sum(self.wordCounters[network][source][word].itervalues())
            result = "The word \"{}\" has been said {} times.".format(word, total)
            if result > 0:
                top = max(self.wordCounters[network][source][word].iteritems(), key=operator.itemgetter(1))
                result = "{} The top contributor is {} with {} times.".format(result, top[0], top[1])
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, result)

    def countMessage(self, server, channel, user, body):
        self._countWords(networkName(self.bot, server), channel.name, user.nick, body)

    def countAction(self, server, source, user, body):
        if body.upper().startswith("ACTION") and isinstance(source, IRCChannel):
            self._countWords(networkName(self.bot, server), source.name, user.nick, body)

    def _countWords(self, server, source, user, body):
        if self.commandUsed:
            self.commandUsed = False
            return
        if server not in self.wordCounters:
            return
        if source not in self.wordCounters[server]:
            return
        for word, users in self.wordCounters[server][source].iteritems():
            if word in body:
                if user in users:
                    self.wordCounters[server][source][word][user] += 1
                else:
                    self.wordCounters[server][source][word][user] = 1
                self.bot.storage["wordcounts"] = self.wordCounters

wordCounter = WordCounterCommand()

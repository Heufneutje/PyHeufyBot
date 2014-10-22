from twisted.words.protocols import irc
from heufybot.channel import IRCChannel
from heufybot.user import IRCUser
from heufybot.utils import isNumber, ModeType


class InputHandler(object):
    def __init__(self, connection):
        self.connection = connection

    def handleCommand(self, command, prefix, params):
        if isNumber(command):
            self._handleNumeric(command, prefix, params)
        elif command == "JOIN":
            nick = prefix[:prefix.find("!")]
            ident = prefix[prefix.find("!") + 1:prefix.find("@")]
            host = prefix[prefix.find("@") + 1:]
            if nick not in self.connection.users:
                user = IRCUser(nick, ident, host)
                self.connection.users[nick] = user
            else:
                user = self.connection.users[nick]
            if params[0] not in self.connection.channels:
                channel = IRCChannel(params[0])
                self.connection.channels[params[0]] = channel
            else:
                channel = self.connection.channels[params[0]]
            channel.users[nick] = user
            channel.ranks[nick] = ""
            self.connection.bot.moduleHandler.runGenericAction("channeljoin", channel)
        elif command == "PING":
            self.connection.outputHandler.cmdPONG(" ".join(params))

    def _handleNumeric(self, numeric, prefix, params):
        if numeric == irc.RPL_WELCOME:
            self.connection.loggedIn = True
            self.connection.bot.moduleHandler.runGenericAction("welcome", self.connection.name)
        elif numeric == irc.RPL_MYINFO:
            self.connection.supportHelper.serverName = params[1]
            self.connection.supportHelper.serverVersion = params[2]
            self.connection.supportHelper.userModes = params[3]
        elif numeric == irc.RPL_ISUPPORT:
            tokens = {}
            # The first param is our prefix and the last one is ":are supported by this server"
            for param in params[1:len(params) - 1]:
                keyValuePair = param.split("=")
                if len(keyValuePair) > 1:
                    tokens[keyValuePair[0]] = keyValuePair[1]
                else:
                    tokens[keyValuePair[0]] = ""
            if "CHANTYPES" in tokens:
                self.connection.supportHelper.chanTypes = tokens["CHANTYPES"]
            if "CHANMODES" in tokens:
                self.connection.supportHelper.chanModes.clear()
                groups = tokens["CHANMODES"].split(",")
                for mode in groups[0]:
                    self.connection.supportHelper.chanModes[mode] = ModeType.LIST
                for mode in groups[1]:
                    self.connection.supportHelper.chanModes[mode] = ModeType.PARAM_UNSET
                for mode in groups[2]:
                    self.connection.supportHelper.chanModes[mode] = ModeType.PARAM_SET
                for mode in groups[3]:
                    self.connection.supportHelper.chanModes[mode] = ModeType.NO_PARAM
            if "NETWORK" in tokens:
                self.connection.supportHelper.network = tokens["NETWORK"]
            if "PREFIX" in tokens:
                self.connection.supportHelper.statusModes.clear()
                self.connection.supportHelper.statusSymbols.clear()
                modes = tokens["PREFIX"][1:tokens["PREFIX"].find(")")]
                symbols = tokens["PREFIX"][tokens["PREFIX"].find(")") + 1:]
                self.connection.supportHelper.statusOrder = modes
                for i in range(len(modes)):
                    self.connection.supportHelper.statusModes[modes[i]] = symbols[i]
                    self.connection.supportHelper.statusSymbols[symbols[i]] = modes[i]
            self.connection.supportHelper.rawTokens.update(tokens)

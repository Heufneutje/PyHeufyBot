from twisted.words.protocols import irc
from heufybot.utils import isNumber, ModeType


class InputHandler(object):
    def __init__(self, connection):
        self.connection = connection

    def handleCommand(self, command, prefix, params):
        if isNumber(command):
            self._handleNumeric(command, prefix, params)
        elif command == "PING":
            self.connection.outputHandler.cmdPONG(" ".join(params))

    def _handleNumeric(self, numeric, prefix, params):
        if numeric == irc.RPL_WELCOME:
            self.connection.loggedIn = True
        elif numeric == irc.RPL_MYINFO:
            self.connection.supportHelper.serverName = params[1]
            self.connection.supportHelper.serverVersion = params[2]
            self.connection.supportHelper.userModes = params[3]
        elif numeric == irc.RPL_ISUPPORT:
            tokens = {}
            # The first param is our prefix and the last one is ":are supported by this server"
            for param in params[1:len(params) - 1]:
                keyValuePair = param.split("=")
                tokens[keyValuePair[0]] = keyValuePair[1]
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

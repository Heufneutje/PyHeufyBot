from twisted.plugin import IPlugin, getPlugins
from heufybot.channel import IRCChannel
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements
import heufybot.modules, re


class AliasCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Alias"
    moduleTriggers = ["addalias", "delalias", "showalias", "setaliashelp"]
    aliases = {}

    def triggers(self):
        return self.moduleTriggers + self.aliases.keys()

    def load(self):
        if "aliases" not in self.bot.storage:
            self.bot.storage["aliases"] = {}
        self.aliases = self.bot.storage["aliases"]
        self.help = "Commands: addalias <aliasname> <command/alias> (<params>), delalias <alias>, showalias <alias>, " \
                    "setaliashelp <alias> <helptext> | Add, remove or display command aliases or set a help text on " \
                    "them."
        self.commandHelp = {
            "addalias": "addalias <aliasname> <command/alias> (<params>) | Add an alias with the given name for the "
                        "given command or alias. The position of the parameters can be specified with $<paramnumber> "
                        "or $0 to include the full parameter string. $sender and $channel can also be specified. "
                        "Requires admin permission.",
            "delalias": "delalias <alias> | Delete a given alias. Requires admin permission.",
            "showalias": "showalias <alias> | Display what a given alias is aliased to.",
            "setaliashelp": "setaliashelp <alias> <helptext> | Set the help text for the given alias. Requires admin "
                            "permission."
        }
        for aliasName, aliasDefinition in self.aliases.iteritems():
            helpText = aliasDefinition["helptext"]
            if not helpText:
                helpText = self._getAliasReplacementMessage(aliasName)
                self.commandHelp[aliasName] = helpText

    def checkPermissions(self, server, source, user, command):
        if command in self.moduleTriggers and command != "showalias":
            return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user, "alias")
        return True

    def execute(self, server, source, command, params, data):
        if command == "addalias":
            if len(params) < 2:
                self.replyPRIVMSG(server, source, "Add which alias?")
                return
            alias = params[0].lower()
            if alias in self.aliases:
                self.replyPRIVMSG(server, source, "{!r} already exists as an alias.".format(alias))
                return
            commandsList = []
            for module in getPlugins(IBotModule, heufybot.modules):
                if isinstance(module, BotCommand):
                    commandsList += module.triggers()
            if alias in commandsList:
                self.replyPRIVMSG(server, source, "{!r} already exists as a command.".format(alias))
                return
            if params[1] not in commandsList:
                self.replyPRIVMSG(server, source, "{!r} is not a valid command or alias.".format(params[1]))
                return
            replacement = " ".join(params[1:])
            self.aliases[alias] = {
                "replacement": replacement,
                "helptext": None
            }
            self.commandHelp[alias] = self._getAliasReplacementMessage(alias)
            self._syncAliases()
            self.replyPRIVMSG(server, source, "{!r} has been added as an alias for {!r}.".format(alias, replacement))
        elif command == "delalias":
            if len(params) < 1:
                self.replyPRIVMSG(server, source, "Remove which alias?")
                return
            alias = params[0].lower()
            if self._checkAliasExists(alias, server, source):
                del self.aliases[alias]
                if alias in self.commandHelp:
                    del self.commandHelp[alias]
                self._syncAliases()
                self.replyPRIVMSG(server, source, "Alias {!r} has been removed.".format(alias))
        elif command == "showalias":
            if len(params) < 1:
                self.replyPRIVMSG(server, source, "Add help for which alias?")
                return
            alias = params[0].lower()
            if self._checkAliasExists(alias, server, source):
                self.replyPRIVMSG(server, source, self._getAliasReplacementMessage(alias))
        elif command == "setaliashelp":
            if len(params) < 2:
                self.replyPRIVMSG(server, source, "Add help to which alias?")
                return
            alias = params[0].lower()
            if self._checkAliasExists(alias, server, source):
                helpText = " ".join(params[1:])
                self.aliases[alias]["helptext"] = helpText
                self.commandHelp[alias] = helpText
                self._syncAliases()
                self.replyPRIVMSG(server, source, "Help text for {!r} has been set to {!r}.".format(alias, helpText))
        else:
            src = data["channel"] if "channel" in data else data["user"]
            message = self._getAliasedMessage(server, src, data["user"], command, params)
            if message:
                if "channel" in data:
                    self.bot.moduleHandler.runGenericAction("message-channel", server, src, data["user"], message)
                else:
                    self.bot.moduleHandler.runGenericAction("message-user", server, src, message)

    def _syncAliases(self):
        self.bot.storage["aliases"] = self.aliases

    def _checkAliasExists(self, alias, server, source):
        if alias not in self.aliases:
            self.replyPRIVMSG(server, source, "{!r} is not a valid alias.".format(alias))
            return False
        return True

    def _getAliasReplacementMessage(self, alias):
        return "{!r} is aliased to {!r}.".format(alias, self.aliases[alias]["replacement"])

    def _getAliasedMessage(self, server, source, user, command, params):
        if command.lower() not in self.aliases:
            return None

        replacement = self.aliases[command]["replacement"]
        newMsg = "{}{}".format(self.bot.config.serverItemWithDefault(server, "command_prefix", "!"), replacement)
        newMsg = newMsg.replace("$sender", user.nick)
        if isinstance(source, IRCChannel):
            newMsg = newMsg.replace("$channel", source.name)
        else:
            newMsg = newMsg.replace("$channel", user.nick)

        paramList = [self._mangleReplacementPoints(param) for param in params]

        # If the alias contains numbered param replacement points, replace them.
        if re.search(r'\$[0-9]+', newMsg):
            newMsg = newMsg.replace("$0", " ".join(paramList))
            for i, param in enumerate(paramList):
                if newMsg.find("${}+".format(i + 1)) != -1:
                    newMsg = newMsg.replace("${}+".format(i + 1), " ".join(paramList[i:]))
                else:
                    newMsg = newMsg.replace("${}".format(i + 1), param)
        # If there are no numbered replacement points, append the full parameter list instead.
        else:
            newMsg += " {}".format(" ".join(paramList))

        newMsg = self._unmangleReplacementPoints(newMsg)
        return newMsg

    @staticmethod
    def _mangleReplacementPoints(string):
        # Replace alias replacement points with something that should never show up in messages/responses.
        string = re.sub(r'\$([\w]+)', r'@D\1@', string)
        return string

    @staticmethod
    def _unmangleReplacementPoints(string):
        # Replace the mangled replacement points with unmangled ones.
        string = re.sub(r'@D([\w]+)@', r'$\1', string)
        return string


aliasCommand = AliasCommand()

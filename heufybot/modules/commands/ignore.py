from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import networkName
from zope.interface import implements
from fnmatch import fnmatch


class IgnoreCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Ignore"

    def triggers(self):
        return ["ignore", "unignore"]

    def actions(self):
        return super(IgnoreCommand, self).actions() + [
            ("botmessage", 50, self.applyIgnores) ]

    def applyIgnores(self, data):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, data["server"]):
            return
        if networkName(self.bot, data["server"]) not in self.ignores:
            return
        for ignoredHost in self.ignores[networkName(self.bot, data["server"])]:
            if fnmatch(data["user"].fullUserPrefix().lower(), ignoredHost.lower()):
                data.clear()
                break

    def load(self):
        self.help = "Commands: ignore <hostmask>, unignore <hostmask> | Ignore or unignore a user. Ignored users " \
                    "can't run commands."
        self.commandHelp = {
            "ignore": "ignore <hostmask> | Add a user to the ignore list. Requires admin permission.",
            "unignore": "unignore <hostmask> | Remove a user from the ignore list. Requires admin permission."
        }
        if "ignore_list" not in self.bot.storage:
            self.bot.storage["ignore_list"] = {}
        self.ignores = self.bot.storage["ignore_list"]

    def checkPermissions(self, server, source, user, command):
        return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user, "ignores")

    def execute(self, server, source, command, params, data):
        if networkName(self.bot, server) not in self.ignores:
            self.ignores[networkName(self.bot, server)] = []
        if len(params) == 0:
            if len(self.ignores[networkName(self.bot, server)]) == 0:
                self.replyPRIVMSG(server, source, "There are no users that are ignored.")
            else:
                ignoredUsers = ", ".join(self.ignores[networkName(self.bot, server)])
                self.replyPRIVMSG(server, source, "Ignoring users: {}.".format(ignoredUsers))
            return
        success = []
        fail = []
        if command == "ignore":
            for ignore in params:
                if ignore.lower() in self.ignores[networkName(self.bot, server)]:
                    fail.append(ignore)
                else:
                    self.ignores[networkName(self.bot, server)].append(ignore.lower())
                    success.append(ignore)
            if len(success) > 0:
                self.bot.storage["ignore_list"] = self.ignores
                self.replyPRIVMSG(server, source, "Now ignoring: {}.".format(", ".join(success)))
            if len(fail) > 0:
                self.replyPRIVMSG(server, source, "Already ignored: {}.".format(", ".join(fail)))
        elif command == "unignore":
            for ignore in params:
                if ignore.lower() in self.ignores[networkName(self.bot, server)]:
                    self.ignores[networkName(self.bot, server)].remove(ignore.lower())
                    success.append(ignore)
                else:
                    fail.append(ignore)
            if len(success) > 0:
                self.bot.storage["ignore_list"] = self.ignores
                self.replyPRIVMSG(server, source, "No longer ignoring: {}.".format(", ".join(success)))
            if len(fail) > 0:
                self.replyPRIVMSG(server, source, "Not ignored: {}.".format(", ".join(fail)))


ignoreCommand = IgnoreCommand()

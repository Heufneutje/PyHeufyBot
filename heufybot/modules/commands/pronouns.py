from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import networkName
from zope.interface import implements
import json, os.path


class PronounsCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Pronouns"

    def triggers(self):
        return ["pronouns", "setpron", "rmpron"]

    def actions(self):
        return super(PronounsCommand, self).actions() + [ ("pronouns", 1, self.lookUpPronouns) ]

    def lookUpPronouns(self, server, source, user, displayErrors):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return

        if networkName(self.bot, server) in self.pronstore and user.lower() in self.pronstore[networkName(self.bot,
                                                                                                          server)]:
            return {
                "success": True,
                "pronouns": self.pronstore[networkName(self.bot, server)][user.lower()]
            }
        if displayErrors:
            error = "User's pronouns have not been specified. Your pronouns can be set with the \"setpron\" command, " \
                    "{}".format(user)
            self.replyPRIVMSG(server, source, error)
            return {
                "success": False
            }

    def load(self):
        self.help = "Commands: pronouns <user>, setpron <pronouns>, rmpron | "\
                    "Query the user's pronouns or specify your own."
        self.commandHelp = {
            "pronouns": "pronouns (<user>) | Query a given user's pronouns or your or your own if no user is given.",
            "setpron": "setpron <pronouns> | Set your own pronouns.",
            "rmpron": "rmpron | Remove your pronouns for a mysterious unspeakable reason."
        }
        if "pronouns" not in self.bot.storage:
            self.bot.storage["pronouns"] = {}
        self.pronstore = self.bot.storage["pronouns"]

    def execute(self, server, source, command, params, data):
        if command == "setpron":
            if len(params) < 1:
                self.replyPRIVMSG(server, source, "Your pronouns are ...blank?")
                return
            if networkName(self.bot, server) not in self.pronstore:
                self.pronstore[networkName(self.bot, server)] = {}
            self.pronstore[networkName(self.bot, server)][data["user"].nick.lower()] = " ".join(params)
            self.bot.storage["pronouns"] = self.pronstore  # actually unsure why this is needed
            self.replyPRIVMSG(server, source, "Your pronouns have been noted.")
        elif command == "rmpron":
            if data["user"].nick.lower() not in self.pronstore[networkName(self.bot, server)]:
                self.replyPRIVMSG(server, source, "I don't even know your pronouns!")
            else:
                del self.pronstore[networkName(self.bot, server)][data["user"].nick.lower()]
                self.bot.storage["pronouns"] = self.pronstore
                self.replyPRIVMSG(server, source, "Your pronouns have been removed.")
        elif command == "pronouns":
            if len(params) < 1:
                lookup = data["user"].nick.lower()
            else:
                lookup = params[0]
            userpron = self.lookUpPronouns(server, source, lookup, True)
            if userpron["success"]:
                self.replyPRIVMSG(server, source, "{} uses <{}> pronouns".format(lookup, userpron["pronouns"]))

userProno = PronounsCommand()

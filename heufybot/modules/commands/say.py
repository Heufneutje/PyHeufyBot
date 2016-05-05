from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class SayCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Say"

    def triggers(self):
        return ["say", "sayto", "do", "doto"]

    def load(self):
        self.help = "Commands: say <message>, sayto <target> <message>, do <message>, doto <target> <message> | Make " \
                    "the bot say certain things."
        self.commandHelp = {
            "say": "say <message> | Make the bot say a given thing in the current channel or query.",
            "sayto": "sayto <target> <message> | Make the bot say a given thing in a given location. Requires admin "
                     "permission.",
            "do": "do <message> | Make the bot do a given thing in the current channel or query.",
            "doto": "doto <target> <message> | Make the bot do a given thing in a given location. Requires admin "
                    "permission"
        }

    def checkPermissions(self, server, source, user, command):
        if command == "sayto" or command == "doto":
            return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                                  "bot-conversation")
        return True

    def execute(self, server, source, command, params, data):
        if command == "say" and len(params) < 1 or command == "sayto" and len(params) < 2:
            self.replyPRIVMSG(server, source, "Say what?")
            return
        if command == "do" and len(params) < 1 or command == "doto" and len(params) < 2:
            self.replyPRIVMSG(server, source, "Do what?")
            return
        if command == "say":
            self.replyPRIVMSG(server, source, " ".join(params))
        elif command == "sayto":
            self.replyPRIVMSG(server, params[0], " ".join(params[1:]))
        elif command == "do":
            self.replyACTION(server, source, " ".join(params))
        elif command == "doto":
            self.replyACTION(server, params[0], " ".join(params[1:]))


sayCommand = SayCommand()

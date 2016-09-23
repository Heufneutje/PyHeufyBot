from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class ShortenCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Shorten"

    def triggers(self):
        return ["shorten"]

    def load(self):
        self.help = "Commands: shorten | Shortens a URL using goo.gl."
        self.commandHelp = {}

    def execute(self, server, source, command, params, data):
        if len(params) < 1:
            self.replyPRIVMSG(server, source, "Shorten what?")
            return
        link = self.bot.moduleHandler.runActionUntilValue("shorten-url", params[0])
        if not link:
            self.replyPRIVMSG(server, source, "Something went wrong while shortening the URL.")
        else:
            self.replyPRIVMSG(server, source, link)


shortenCommand = ShortenCommand()

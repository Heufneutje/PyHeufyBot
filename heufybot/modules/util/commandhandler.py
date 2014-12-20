from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class CommandHandler(BotModule):
    implements(IPlugin, IBotModule)

    name = "CommandHandler"

    def hookBot(self, bot):
        self.bot = bot

    def actions(self):
        return [ ("message-channel", 1, self.handleChannelMessage),
                 ("message-user", 1, self.handlePrivateMessage) ]

    def handleChannelMessage(self, server, channel, user, messageBody):
        pass

    def handlePrivateMessage(self, server, user, messageBody):
        pass

    def handleCommand(self, message):
        pass

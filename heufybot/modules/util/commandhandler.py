from twisted.plugin import IPlugin
from heufybot.moduleinterface import BotModule, IBotModule
from zope.interface import implements


class CommandHandler(BotModule):
    implements(IPlugin, IBotModule)

    name = "CommandHandler"

    def actions(self):
        return [ ("message-channel", 1, self.handleChannelMessage),
                 ("message-user", 1, self.handlePrivateMessage) ]

    def handleChannelMessage(self, server, channel, user, messageBody):
        message = {
            "server": server,
            "source": channel.name,
            "channel": channel,
            "user": user,
            "body": messageBody
        }
        self._handleCommand(message)

    def handlePrivateMessage(self, server, user, messageBody):
        message = {
            "server": server,
            "source": user.nick,
            "user": user,
            "body": messageBody
        }
        self._handleCommand(message)

    def _handleCommand(self, message):
        commandPrefix = self.bot.config.serverItemWithDefault(message["server"], "command_prefix", "!")
        if not message["body"].startswith(commandPrefix):
            return # We don't need to be handling things that aren't bot commands
        params = message["body"].split()
        message["command"] = params[0][params[0].index(commandPrefix) + len(commandPrefix):]
        del params[0]
        message["params"] = params
        self.bot.moduleHandler.runProcessingAction("botmessage", message)

commandHandler = CommandHandler()

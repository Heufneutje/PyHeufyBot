from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class ConnectionControlCommands(BotCommand):
    implements(IPlugin, IBotModule)

    name = "ConnectionControl"

    def triggers(self):
        return ["connect", "disconnect", "reconnect", "shutdown", "restart"]

    def load(self):
        self.help = "Commands: connect <server>, disconnect (<server>) (<quitmessage>), reconnect (<server>) (" \
                    "<quitmessage>), shutdown (<quitmessage>), restart (<quitmessage>) | Provides control over the " \
                    "bot's connections."
        self.commandHelp = {
            "connect": "connect <server> | Connect to a server that's defined in the bot's config.",
            "disconnect": "disconnect (<server>) (<quitmessage>) | Disconnect from a server the bot is currently on.",
            "reconnect": "reconnect (<server>) (<quitmessage>) | Reconnect to a server the bot is currently on.",
            "shutdown": "shutdown (<quitmessage>) | Shutdown the bot.",
            "restart": "restart (<quitmessage>) | Perform a full restart of the bot."
        }

    def checkPermissions(self, server, source, user, command):
        return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                              "connection-control")

    def execute(self, server, source, command, params, data):
        message = None
        if command == "connect":
            if len(params) < 1:
                self.replyPRIVMSG(server, source, "Connect where?")
                return
            message = self.bot.connectServer(params[0])
        elif command == "disconnect":
            if len(params) < 1:
                self.bot.disconnectServer(server)
            elif len(params) < 2:
                message = self.bot.disconnectServer(params[0])
            else:
                message = self.bot.disconnectServer(params[0], " ".join(params[1:]))
        elif command == "reconnect":
            if len(params) < 1:
                if len(params) < 1:
                    self.bot.reconnectServer(server)
                elif len(params) < 2:
                    message = self.bot.reconnectServer(params[0])
                else:
                    message = self.bot.reconnectServer(params[0], " ".join(params[1:]))
        elif command == "shutdown":
            if len(params) < 1:
                self.bot.shutdown()
            else:
                self.bot.shutdown(" ".join(params))
        elif command == "restart":
            if len(params) < 1:
                self.bot.restart()
            else:
                self.bot.restart(" ".join(params))
        if message:
            self.replyPRIVMSG(server, source, message)


connectionControlCommands = ConnectionControlCommands()

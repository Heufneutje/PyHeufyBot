from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class ConnectionControlCommands(BotCommand):
    implements(IPlugin, IBotModule)

    name = "ConnectionControl"

    def triggers(self):
        return ["connect", "disconnect", "reconnect", "shutdown", "restart"]

    def checkPermissions(self, server, source, user, command):
        return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                              "connection-control")

    def execute(self, server, source, command, params, data):
        message = None
        if command == "connect":
            if len(params) < 1:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Connect where?")
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
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, message)

connectionControlCommands = ConnectionControlCommands()

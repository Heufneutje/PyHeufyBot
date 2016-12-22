from heufybot.moduleinterface import BotModule
from heufybot.utils.dummycontextmanager import DummyContextManager
from heufybot.utils.signaltimeout import TimeoutException
from traceback import format_exc
import sys

if sys.platform != "win32":
    from heufybot.utils.signaltimeout import SignalTimeout
else:
    SignalTimeout = None


class BotCommand(BotModule):
    name = "UnknownCommand"
    timeout = 5

    def actions(self):
        return [ ("botmessage", 1, self.handleCommand),
                 ("commandhelp", 1, self.displayHelp) ]

    def load(self):
        self.help = "This module does not provide a help text."
        self.commandHelp = {}

    def triggers(self):
        return []

    def handleCommand(self, data):
        if self._shouldExecute(data["server"], data["source"], data["user"], data["command"]):
            try:
                with SignalTimeout(self.timeout) if SignalTimeout is not None else DummyContextManager():
                    self.execute(data["server"], data["source"], data["command"].lower(), data["params"], data)
            except TimeoutException:
                self.replyPRIVMSG(data["server"], data["source"], "The command timed out.")
            except Exception as ex:
                error = "Python execution error while running command: {}: {}".format(type(ex).__name__, ex.message)
                self.replyPRIVMSG(data["server"], data["source"], error)
                self.bot.log.failure("Error while running command:\n {ex}", ex=format_exc())

    def displayHelp(self, server, request):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return None
        request = request.lower()
        if request == self.name.lower():
            return self.help
        if request in [x.lower() for x in self.triggers()]:
            if request in self.commandHelp:
                return self.commandHelp[request]
            else:
                return self.help
        return None

    def replyPRIVMSG(self, server, source, message):
        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, message)

    def replyNOTICE(self, server, source, message):
        self.bot.servers[server].outputHandler.cmdNOTICE(source, message)

    def replyACTION(self, server, source, message):
        self.bot.servers[server].outputHandler.ctcpACTION(source, message)

    def _shouldExecute(self, server, source, user, command):
        if not self.bot.moduleHandler.useModuleOnServer(self.name, server):
            return False
        if command.lower() not in [x.lower() for x in self.triggers()]:
            return False
        if not self.checkPermissions(server, source, user, command.lower()):
            return False
        return True

    def checkPermissions(self, server, source, user, command):
        return True # This function should be implemented by the commands that inherit from this

    def execute(self, server, source, command, params, data):
        pass # This function should be implemented by the commands that inherit from this

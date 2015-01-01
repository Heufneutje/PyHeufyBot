from heufybot.moduleinterface import BotModule


class BotCommand(BotModule):
    name = "UnknownCommand"

    def hookBot(self, bot):
        self.bot = bot

    def actions(self):
        return [ ("botmessage", 1, self._handleCommand) ]

    def triggers(self):
        return []

    def _handleCommand(self, data):
        if self._shouldExecute(data["server"], data["source"], data["user"], data["command"]):
            self.execute(data["server"], data["source"], data["command"].lower(), data["params"], data)

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

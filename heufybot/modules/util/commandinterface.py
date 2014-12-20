from heufybot.moduleinterface import BotModule


class BotCommand(BotModule):
    def hookBot(self, bot):
        self.bot = bot
        self.triggers = []

    def actions(self):
        return [ ("botmessage", 1, self._handleCommand) ]

    def _handleCommand(self, data):
        if self._shouldExecute(data["command"]):
            pass

    def _shouldExecute(self, command):
        if command not in self.triggers:
            return False
        if not self.checkPermissions():
            return False
        return True

    def checkPermissions(self):
        return True # This function should be implemented by the commands that inherit from this

    def execute(self, data):
        pass # This function should be implemented by the commands that inherit from this

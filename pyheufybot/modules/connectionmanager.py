from pyheufybot.moduleinterface import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "ConnectionManager"
        self.trigger = "connect|disconnect|reconnect|restart|quit"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ADMINS
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: connect <server>, disconnect (<server>), reconnect (<server>), restart, quit  | Manages the bot's connections. To connec to a server a config file for that server must be present."

    def execute(self, message):
        botHandler = self.bot.factory.botHandler
        command = message.params[0].lower()
        if command == "disconnect" or command == "reconnect":
            if len(message.params) == 1:
                botHandler.stopFactory(self.bot.factory.config.getSettingWithDefault("server", "irc.foo.bar"), None, True if command == "reconnect" else False)
            elif len(message.params) == 2:
                if not botHandler.stopFactory(message.params[1], None, True if command == "reconnect" else False):
                    self.bot.msg(message.replyTo, "I'm not connected to that server!")
            elif len(message.params) > 2:
                if not botHandler.stopFactory(message.params[1], " ".join(message.params[2:]), True if command == "reconnect" else False):
                    self.bot.msg(message.replyTo, "I'm not connected to that server!")
        return True

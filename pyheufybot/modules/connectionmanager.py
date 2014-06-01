from pyheufybot.modulehandler import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "ConnectionManager"
        self.trigger = "connect|disconnect|reconnect|restart|quit"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ADMINS
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: connect <server>, disconnect (<server>) (<message), reconnect (<server>) (<message>), restart (<message>), quit (<message>)  | Manages the bot's connections. To connect to a server a config file for that server must be present."

    def execute(self, message):
        botHandler = self.bot.factory.botHandler
        command = message.params[0].lower()
        if command == "connect":
            if len(message.params) == 1:
                self.bot.msg(message.replyTo, "What do you want me to connect to?")
            else:
                for config in botHandler.configs:
                    if config.getSettingWithDefault("server", "irc.foo.bar").lower() == message.params[1].lower():
                        if not botHandler.startFactory(config):
                            self.bot.msg(message.replyTo, "I can't join that server because I'm already on it!")
        elif command == "disconnect" or command == "reconnect":
            if len(message.params) == 1:
                botHandler.stopFactory(self.bot.factory.config.getSettingWithDefault("server", "irc.foo.bar"), None, True if command == "reconnect" else False)
            elif len(message.params) == 2:
                if not botHandler.stopFactory(message.params[1], None, True if command == "reconnect" else False):
                    self.bot.msg(message.replyTo, "I'm not connected to that server!")
            elif len(message.params) > 2:
                if not botHandler.stopFactory(message.params[1], " ".join(message.params[2:]), True if command == "reconnect" else False):
                    self.bot.msg(message.replyTo, "I'm not connected to that server!")
        elif command == "quit" or command == "restart":
            quitMessage = " ".join(message.params[1:]) if len(message.params) > 1 else None
            restart = True if command == "restart" else False
            botHandler.quit(quitMessage, restart)
        return True

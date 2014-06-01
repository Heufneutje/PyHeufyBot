import random
from pyheufybot.modulehandler import Module, ModuleAccessLevel, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        super(ModuleSpawner, self).__init__(bot)

        self.name = "Choose"
        self.trigger = "choose|choice"
        self.moduleType = ModuleType.COMMAND
        self.modulePriority = ModulePriority.NORMAL
        self.accessLevel = ModuleAccessLevel.ANYONE
        self.messageTypes = ["PRIVMSG"]
        self.helpText = "Usage: choose <option1>, <option2>, ...  | Makes the bot choose one of the given options."

    def execute(self, message):
        if len(message.params) == 1:
            self.bot.msg(message.replyTo, "What do you want me to choose from?")
        else:
            params = " ".join(message.params[1:])
            if ',' in params:
                options = params.split(',')
            else:
                options = params.split()
            self.bot.msg(message.replyTo, "Choice: {}".format(random.choice(options).strip()))

        return True

from pyheufybot.module_interface import Module, ModulePriority, ModuleType

class ModuleSpawner(Module):
    def __init__(self, bot):
        self.bot = bot
        self.name = "NickServIdentify"
        self.moduleType = ModuleType.PASSIVE
        self.modulePriority = ModulePriority.NORMAL
        self.messageTypes = ["USER"]
        self.helpText = "Attempts to log into NickServ with the password in the config."

    def execute(self, message):
        config = self.bot.factory.config
        passwordType = config.getSettingWithDefault("passwordType", None)
        password = config.getSettingWithDefault("password", "")

        if passwordType == "NickServ":
            self.bot.msg("NickServ", "IDENTIFY {}".format(password), None, False)
        return True

from pyheufybot.module_interface import Module, ModuleType
from pyheufybot.message import IRCResponse, ResponseType
from pyheufybot import globalvars

class ModuleSpawner(Module):
    def __init__(self):
        self.name = "NickServIdentify"
        self.moduleType = ModuleType.PASSIVE
        self.messageTypes = ["USER"]
        self.helpText = "Attempts to log into NickServ with the password in the config"

    def execute(self, message):
        config = globalvars.botHandler.factories[message.serverInfo.name].config
        passwordType = config.getSettingWithDefault("passwordType", None)
        password = config.getSettingWithDefault("password", "")

        if passwordType == "NickServ":
            return [ IRCResponse("NickServ", "IDENTIFY " + password, ResponseType.MESSAGE) ]
        else:
            return []

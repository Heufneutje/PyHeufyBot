from pyheufybot.module_interface import Module, ModuleType
from pyheufybot.message import IRCResponse, ResponseType
from pyheufybot import globalvars

class NickServIdentify(Module):
    def __init__(self):
        self.moduleType = ModuleType.PASSIVE
        self.messageTypes = ["USER"]
        self.helpText = "Attempts to log into NickServ with the password in the config"

    def execute(self, message, serverInfo):
        config = globalvars.botHandler.factories[serverInfo.name].config
        passwordType = config.getSettingWithDefault("passwordType", None)
        password = config.getSettingWithDefault("password", "")

        if passwordType == "NickServ":
            return [ IRCResponse("NickServ", "IDENTIFY " + password, responseType.MESSAGE) ]
        else:
            return []

from module_interface import Module, ModuleType
from message import IRCResponse, ResponseType
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
            return [ IRCResponse("NickServ", responseType.MESSAGE, password) ]
        else:
            return []

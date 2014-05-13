from pyheufybot.message import IRCMessage, IRCResponse, ResponseType
from pyheufybot.serverinfo import ServerInfo
from enum import Enum

class Module(object):
    def __init__(self):
        self.name = None
        self.trigger = ""
        self.moduleType = ModuleType.PASSIVE
        self.messageTypes = []
        self.helpText = "No help available for this module"

    def excecute(self, message, serverInfo):
        pass

    def onModuleLoaded(self):
        pass

    def onModuleUnloaded(self):
        pass

class ModuleInterface(object):
    def __init__(self, bot):
        self.bot = bot
        self.modules = []

    def loadModule(self, moduleName):
        pass

    def unloadModule(self, moduleName):
        pass

    def shouldExecute(self, module, message):
        pass

    def handleMessage(self, message):
        pass

    def sendResponses(self, responses):
        for response in responses:
            if response.responseType == ResponseType.MESSAGE:
                self.bot.msg(response.target, response.responseText)
            elif response.responseType == ResponseType.ACTION:
                self.bot.msg(response.target, response.responseText)
            elif response.responseType == ResponseType.NOTICE:
                self.bot.notice(response.target, response.responseText)
            elif response.responseType == ResponseType.RAW:
                self.bot.sendLine(response.responseText)

class ModuleType(Enum):
    ACTIVE = 1
    PASSIVE = 2
    TRIGGERED = 3

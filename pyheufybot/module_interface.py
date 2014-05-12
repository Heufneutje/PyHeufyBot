from pyheufybot.message import IRCMessage
from pyheufybot.serverinfo import ServerInfo
from enum import Enum

class Module(object):
    def __init__(self):
        self.trigger = ""
        self.moduleType = ModuleType.PASSIVE
        self.messageTypes = []
        self.helpText = "No help available for this module"

    def excecute(self, message=IRCMessage, serverInfo=ServerInfo):
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

    def shouldExecute(self, module=Module, message=IRCMessage):
        pass

    def handleMessage(self, message=IRCMessage):
        pass

class ModuleType(Enum):
    ACTIVE = 1
    PASSIVE = 2
    TRIGGERED = 3

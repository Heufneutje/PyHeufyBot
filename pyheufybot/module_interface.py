import importlib, os, re, sys
from pyheufybot.logger import log
from pyheufybot.message import IRCMessage
from pyheufybot.serverinfo import ServerInfo
from enum import Enum
from glob import glob

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        self.name = None
        self.trigger = ""
        self.moduleType = ModuleType.PASSIVE
        self.messageTypes = []
        self.helpText = "No help available for this module"

    def excecute(self, message):
        pass

    def onModuleLoaded(self):
        pass

    def onModuleUnloaded(self):
        pass

class ModuleInterface(object):
    def __init__(self, bot):
        self.bot = bot
        self.modules = {}
        self.commandPrefix = bot.factory.config.getSettingWithDefault("commandPrefix", "!")

    def loadModule(self, moduleName):
        moduleName = moduleName.lower()

        # Check if the module is loaded already.
        if moduleName in self.modules:
            return [False, "Module \"{}\" is already loaded.".format(self.modules[moduleName].name)]

        # Try to load the module
        try:
            src = importlib.import_module("pyheufybot.modules.{}".format(moduleName))
        except ImportError as e:
            errorMsg = "Module \"{}\" could not be loaded ({}).".format(moduleName, e)
            log("*** ERROR: {}".format(errorMsg), None)
            return [False, errorMsg]
        
        reload(src)

        try:
            module = src.ModuleSpawner(self.bot)
            self.modules[moduleName] = module
            module.onModuleLoaded()
            log("->- Loaded module \"{}\".".format(module.name), None)
        except Exception as e:
            errorMsg = "An exception occurred while loading module \"{}\" ({}).".format(moduleName, e)
            log("*** ERROR: {}".format(errorMsg), None)
            return [False, errorMsg]

        return [True, module.name]

    def unloadModule(self, moduleName):
        moduleName = moduleName.lower()
        
        if moduleName in self.modules:
            try:
                module = self.modules[moduleName]
                module.onModuleUnloaded()
                del self.modules[moduleName]
                del sys.modules["pyheufybot.modules.{}".format(moduleName)]
                for f in glob("pyheufybot/modules/{}.pyc".format(moduleName)):
                    os.remove(f)
                log("-<- Unloaded module \"{}\".".format(module.name), None)
                return [True, module.name]
            except Exception as e:
                errorMsg = "An exception occurred while unloading module \"{}\" ({}).".format(moduleName, e)
                log("*** ERROR: {}".format(errorMsg), None)
                return [False, errorMsg]
        else: 
            return [False, "Module \"{}\" is not loaded or doesn't exist.".format(moduleName)]

    def reloadModule(self, moduleName):
        moduleName = moduleName.lower()

        result = self.unloadModule(moduleName)
        if not result[0]:
            return [False, result[1]]

        result = self.loadModule(moduleName)
        if not result[0]:
            return [False, result[1]]

        return [True, result[1]]

    def loadAllModules(self):
        log("--- Loading modules...", None)
        modules = self.bot.factory.config.getSettingWithDefault("modules", [])
        for module in modules:
            self.loadModule(module)

    def unloadAllModules(self):
        log("--- Unloading modules...", None)
        for module in self.modules:
            self.unloadModule(module)

    def shouldExecute(self, module, message):
        if message.messageType in module.messageTypes:
            if module.moduleType == ModuleType.PASSIVE:
                return True
            elif message.user.nickname == self.bot.nickname:
                return False
            elif module.moduleType == ModuleType.TRIGGER:
                match = re.search(".*{}.*".format(module.trigger), message.messageText, re.IGNORECASE)
                return True if match else False
            elif module.moduleType == ModuleType.COMMAND:
                match = re.search("^{}{} .*".format(self.commandPrefix, module.trigger), message.messageText, re.IGNORECASE)
                return True if match else False

    def handleMessage(self, message):
        for module in self.modules.values():
            if self.shouldExecute(module, message):
                if module.moduleType == ModuleType.COMMAND:
                    # Strip the command prefix before passing
                    newMessage = IRCMessage(message.messageType, message.user, message.channel, message.messageText[len(self.commandPrefix):])
                    module.execute(newMessage)
                else:
                    module.execute(message)

class ModuleType(Enum):
    COMMAND = 1
    PASSIVE = 2
    TRIGGER = 3

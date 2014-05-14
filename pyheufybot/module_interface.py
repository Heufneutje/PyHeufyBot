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

    def loadModule(self, moduleName):
        moduleName = moduleName.lower()

        # Check if the module is loaded already.
        if moduleName in self.modules:
            # Module is already loaded. Try to unload it so it can be reloaded.
            if not self.unloadModule(moduleName):
                return False

        # Try to load the module
        try:
            src = importlib.import_module("pyheufybot.modules." + moduleName)
        except ImportError as e:
            log("*** ERROR: Module \"{}\" could not be loaded ({}).".format(moduleName, e), None)
            return False
        
        reload(src)

        try:
            module = src.ModuleSpawner(self.bot)
            self.modules[moduleName] = module
            module.onModuleLoaded()
            log("--- Loaded module \"{}\".".format(module.name), None)
        except Exception as e:
            log("*** ERROR: An error occurred while loading module \"{}\" ({}).".format(moduleName, e), None)
            return False

        return True

    def unloadModule(self, moduleName):
        moduleName = moduleName.lower()
        
        if moduleName in self.modules:
            try:
                module = self.modules[moduleName]
                module.onUnloadModule()
                del self.modules[moduleName]
                del sys.modules["pyheufybot.modules.{}".format(moduleName)]
                for f in glob("pyheufybot/modules/{}.pyc".format(moduleName)):
                    os.remove(f)
                log("--- Unloaded module \"{}\".".format(module.name), None)
                return True
            except Exception as e:
                log("*** ERROR: An error occurred while unloading module \"{}\" ({}).".format(moduleName, e), None)
                return False

    def loadAllModules(self):
        log("--- Loading modules...", None)
        modules = self.bot.factory.config.getSettingWithDefault("modules", [])
        for module in modules:
            self.loadModule(module)

    def shouldExecute(self, module, message):
        if message.messageType in module.messageTypes:
            if module.moduleType == ModuleType.PASSIVE:
                return True
            elif module.moduleType == ModuleType.TRIGGER:
                match = re.search(".*{}.*".format(module.trigger), message.messageText, re.IGNORECASE)
                return True if match else False
            elif module.moduleType == ModuleType.COMMAND:
                commandPrefix = self.bot.factory.config.getSettingWithDefault("commandPrefix", "!")
                match = re.search("^{}{}.*".format(commandPrefix, module.trigger), message.messageText, re.IGNORECASE)
                return True if match else False

    def handleMessage(self, message):
        for module in self.modules.values():
            if self.shouldExecute(module, message):
                module.execute(message)

class ModuleType(Enum):
    COMMAND = 1
    PASSIVE = 2
    TRIGGER = 3

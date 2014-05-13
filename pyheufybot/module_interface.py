import imp, re
from pyheufybot.logger import log
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

        # Try to find the module.
        try:
            search = imp.find_module("pyheufybot/modules/{}".format(moduleName))
        except ImportError as e:
            log("*** ERROR: Module \"{}\" could not be found ({}).".format(moduleName, e), None)
            return False
        
        # Module has been found. Let's try to import it.
        try:
            load = imp.load_module(moduleName, search[0], search[1], search[2])
        except ImportError as e:
            log("*** ERROR: Module \"{}\" could not be loaded ({}).".format(moduleName, e), None)
            search[0].close()
            return False
        
        # Module has been imported. Try to load it and add it to the modules dictionary.
        search[0].close()
        try:
            module = load.ModuleSpawner()
            self.modules[moduleName] = module
            module.onModuleLoaded()
            log("*** Loaded module \"{}\".".format(module.name), None)
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
                log("*** Unloaded module \"{}\".".format(module.name), None)
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
            elif module.moduleType == ModuleType.TRIGGERED:
                match = re.search(".*{}.*".format(module.trigger), message.messageText, re.IGNORECASE)
                return match
            else:
                commandPrefix = self.bot.config.getSettingWithDefault("commandPrefix", "!")
                match = re.search("^{}{}.*".format(commandPrefix, module.trigger), message.messageText, re.IGNORECASE)
                return match

    def handleMessage(self, message):
        print "test"
        for module in self.modules.values():
            if self.shouldExecute(module, message):
                module.execute(message)

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

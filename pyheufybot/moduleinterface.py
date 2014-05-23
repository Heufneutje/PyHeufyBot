import importlib, operator, os, re, sys, traceback
from pyheufybot.logger import log
from pyheufybot.message import IRCMessage
from pyheufybot.utils.fileutils import createDirs
from enum import Enum
from glob import glob

class Module(object):
    def __init__(self, bot):
        self.bot = bot
        self.name = None
        self.trigger = ""
        self.moduleType = ModuleType.PASSIVE
        self.modulePriority = ModulePriority.NORMAL
        self.messageTypes = []
        self.helpText = "No help available for this module."

    def excecute(self, message):
        pass

    def onModuleLoaded(self):
        pass

    def onModuleUnloaded(self):
        pass

    def reloadData(self):
        pass

    def getHelp(self, command):
        return self.helpText

class ModuleInterface(object):
    def __init__(self, bot):
        self.bot = bot
        self.modules = {}
        self.server = bot.factory.config.getSettingWithDefault("server", "irc.foo.bar")
        self.commandPrefix = bot.factory.config.getSettingWithDefault("commandPrefix", "!")
        createDirs(os.path.join("data", self.server))
        self.dataPath = os.path.join("data", self.server)

    def loadModule(self, moduleName):
        moduleName = moduleName.lower()

        # Check if the module is loaded already.
        if moduleName in self.modules:
            return [False, "Module \"{}\" is already loaded.".format(self.modules[moduleName].name)]

        # Try to load the module
        try:
            src = importlib.import_module("pyheufybot.modules.{}".format(moduleName))
        except (ImportError, SyntaxError, AttributeError) as e:
            errorMsg = "Module \"{}\" could not be loaded ({}).".format(moduleName, e)
            log("[{}] ERROR: {}".format(self.server, errorMsg), None)
            return [False, errorMsg]
        
        reload(src)

        try:
            module = src.ModuleSpawner(self.bot)

            # Check if the module has all the required fields.
            errorMsg = "Module \"{}\" is missing one or more of the required fields and cannot be loaded.".format(moduleName)
            if not (hasattr(module, "name") and hasattr(module, "moduleType") and hasattr(module, "modulePriority") and hasattr(module, "messageTypes") and hasattr(module, "helpText")):
                log("[{}] ERROR: {}".format(self.server, errorMsg), None)
                return [False, errorMsg]
                if module.moduleType == ModuleType.COMMAND:
                    if not hasattr(module, "trigger"):
                        log("[{}] ERROR: {}".format(self.server, errorMsg), None)
                        return [False, errorMsg]

            # Module is valid and can be loaded.
            self.modules[moduleName] = module
            module.onModuleLoaded()
            log("[{}] ->- Loaded module \"{}\".".format(self.server, module.name), None)
        except Exception as e:
            errorMsg = "An exception occurred while loading module \"{}\" ({}).".format(moduleName, e)
            log("[{}] ERROR: {}".format(self.server, errorMsg), None)
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
                log("[{}] -<- Unloaded module \"{}\".".format(self.server, module.name), None)
                return [True, module.name]
            except Exception as e:
                errorMsg = "An exception occurred while unloading module \"{}\" ({}).".format(moduleName, e)
                log("[{}] ERROR: {}".format(self.server, errorMsg), None)
                del self.modules[moduleName]
                del sys.modules["pyheufybot.modules.{}".format(moduleName)]
                for f in glob("pyheufybot/modules/{}.pyc".format(moduleName)):
                    os.remove(f)
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
        log("[{}] --- Loading modules...".format(self.server), None)
        modules = self.bot.factory.config.getSettingWithDefault("modules", [])
        for module in modules:
            self.loadModule(module)

    def unloadAllModules(self):
        log("[{}] --- Unloading modules...".format(self.server), None)
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
                match = re.search("^{}({})($| .*)".format(self.commandPrefix, module.trigger), message.messageText.lower(), re.IGNORECASE)
                return True if match else False

    def handleMessage(self, message):
        try:
            noInterrupt = True
            for module in sorted(self.modules.values(), key=operator.attrgetter("modulePriority")):
                if not noInterrupt:
                    break
                if self.shouldExecute(module, message):
                    if module.moduleType == ModuleType.COMMAND:
                        # Strip the command prefix before passing
                        newMessage = IRCMessage(message.messageType, message.user, message.channel, message.messageText[len(self.commandPrefix):])
                        noInterrupt = module.execute(newMessage)
                    else:
                        noInterrupt = module.execute(message)
        except (Exception, SyntaxError, AttributeError):
            errorMsg = "An error occurred while handling message \"{}\" ({})".format(message.messageText, sys.exc_info()[1])
            traceback.print_tb(sys.exc_info()[2])
            self.bot.msg(message.replyTo, errorMsg)

    def reloadModuleData(self, modules):
        for module in modules:
            module = module.lower()
            if module in self.modules:
                self.modules[module].reloadData()

class ModuleType(Enum):
    COMMAND = 1
    PASSIVE = 2
    TRIGGER = 3

class ModulePriority(object):
    HIGH = -2
    ABOVENORMAL = -1
    NORMAL = 0
    BELOWNORMAL = -1
    LOW = -2

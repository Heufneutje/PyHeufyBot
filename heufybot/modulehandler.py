from twisted.plugin import getPlugins
from twisted.plugin import log
from twisted.python.rebuild import rebuild
from heufybot.moduleinterface import IBotModule
import heufybot.modules, importlib, logging


class ModuleHandler(object):
    def __init__(self, bot):
        self.bot = bot
        self.modules = []
        self.actions = []

    def loadModule(self, name):
        for module in getPlugins(IBotModule, heufybot.modules):
            if not module.name:
                raise ModuleLoaderError("???", "Module did not provide a name")
            if module.name == name:
                rebuild(importlib.import_module(module.__module__))
                self._loadModuleData(module)
                break

    def _loadModuleData(self, module):
        # Make sure the module meets the requirements and is not already loaded
        if not IBotModule.providedBy(module):
            raise ModuleLoaderError("???", "Module doesn't implement the module interface")
        if module.name in self.modules:
            raise ModuleLoaderError(module.name, "Module is already loaded")
        # We're good at this point so we can start initializing the module now
        module.hookBot(self.bot)

    def unloadModule(self, name):
        pass

    def reloadModule(self, name):
        pass

    def _loadAllModules(self):
        requestedModules = self.bot.config.itemWithDefault("modules", [])
        for module in getPlugins(IBotModule, heufybot.modules):
            if module.name in self.modules:
                continue
            if module.core or module.name in requestedModules:
                self._loadModuleData(module)
        for module in requestedModules:
            if module not in self.modules:
                log.err("Module {} failed to load.".format(module), level=logging.ERROR)

class ModuleLoaderError(Exception):
    def __init__(self, module, message):
        self.module = module
        self.message = message

    def __str__(self):
        return "Module {} could not be loaded/unloaded: {}".format(self.module, self.message)

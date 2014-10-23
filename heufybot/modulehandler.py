from twisted.plugin import getPlugins
from twisted.plugin import log
from twisted.python.rebuild import rebuild
from heufybot.moduleinterface import IBotModule
import heufybot.modules, importlib, logging


class ModuleHandler(object):
    def __init__(self, bot):
        self.bot = bot
        self.loadedModules = {}
        self.actions = {}

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
        if module.name in self.loadedModules:
            raise ModuleLoaderError(module.name, "Module is already loaded")

        # We're good at this point so we can start initializing the module now
        module.hookBot(self.bot)
        actions = {}
        for action in module.actions():
            if action[0] not in actions:
                actions[action[0]] = [ (action[2], action[1]) ]
            else:
                actions[action[0]].append((action[2], action[1]))

        # Add the actions implemented by the module and sort them by priority
        for action, actionList in actions.iteritems():
            if action not in self.actions:
                self.actions[action] = []
                for actionData in actionList:
                    for index, handlerData in enumerate(actions[action]):
                        if handlerData[1] < actionData[1]:
                            self.actions[action].insert(index, actionData)
                            break
                        else:
                            self.actions[action].append(actionData)

        # Add the module to the list of loaded modules and call its load hooks
        self.loadedModules[module.name] = module
        module.load()
        self.runGenericAction("moduleload", module.name)

    def unloadModule(self, name, fullUnload=True):
        if name not in self.loadedModules:
            raise ModuleLoaderError(name, "The module is not loaded")
        module = self.loadedModules[name]
        if module.core and fullUnload:
            raise ModuleLoaderError(name, "Core modules cannot be unloaded")
        module.unload()
        self.runGenericAction("moduleunload", module.name)
        for action in module.actions():
            self.actions[action[0]].remove((action[2], action[1]))
        del self.loadedModules[name]

    def reloadModule(self, name):
        self.unloadModule(name, False)
        self.loadModule(name)

    def loadAllModules(self):
        requestedModules = self.bot.config.itemWithDefault("modules", [])
        for module in getPlugins(IBotModule, heufybot.modules):
            if module.name in self.loadedModules:
                continue
            if module.core or module.name in requestedModules:
                self._loadModuleData(module)
        for module in requestedModules:
            if module not in self.loadedModules:
                log.msg("Module {} failed to load.".format(module), level=logging.ERROR)

    def runGenericAction(self, actionName, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            action[0](*params, **kw)

class ModuleLoaderError(Exception):
    def __init__(self, module, message):
        self.module = module
        self.message = message

    def __str__(self):
        return "Module {} could not be loaded/unloaded: {}".format(self.module, self.message)

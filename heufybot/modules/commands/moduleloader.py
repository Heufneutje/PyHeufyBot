from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modulehandler import ModuleLoaderError
from heufybot.modules.commandinterface import BotCommand
from zope.interface import implements


class ModuleLoaderCommands(BotCommand):
    implements(IPlugin, IBotModule)

    name = "ModuleLoader"

    def triggers(self):
        return ["load", "unload", "reload", "enable", "disable"]

    def load(self):
        self.help = "Commands: load <module>, unload <module>, reload <module>, enable <module>, disable <module> | " \
                    "Provides control over what modules are loaded."
        self.commandHelp = {
            "load": "load <module> | Load a given module.",
            "unload": "unload <module> | Unload a given module.",
            "reload": "reload <module> | Reload a given module.",
            "enable": "enable <module> | Enable a given module for the current server",
            "disable": "disable <module> | Disable a given module for the current server"
        }

    def checkPermissions(self, server, source, user, command):
        return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                              "module-control")

    def execute(self, server, source, command, params, data):
        output = self.bot.servers[server].outputHandler
        if command == "load" and len(params) < 1:
            output.cmdPRIVMSG(source, "Load what?")
            return
        elif command == "unload" and len(params) < 1:
            output.cmdPRIVMSG(source, "Unload what?")
            return
        elif command == "reload" and len(params) < 1:
            output.cmdPRIVMSG(source, "Reload what?")
            return
        elif command == "enable" and len(params) < 1:
            output.cmdPRIVMSG(source, "Enable what?")
            return
        elif command == "disable" and len(params) < 1:
            output.cmdPRIVMSG(source, "Disable what?")
            return

        success = []
        failed = []
        for module in params:
            try:
                if command == "load":
                    success.append(self.bot.moduleHandler.loadModule(module))
                elif command == "unload":
                    success.append(self.bot.moduleHandler.unloadModule(module))
                elif command == "reload":
                    success.append(self.bot.moduleHandler.reloadModule(module))
                elif command == "enable":
                    success.append(self.bot.moduleHandler.enableModule(module, server))
                elif command == "disable":
                    success.append(self.bot.moduleHandler.disableModule(module, server))
            except ModuleLoaderError as e:
                failed.append(e)
        if len(success) > 0:
            action = None
            if command == "load":
                action = "loaded"
            elif command == "unload":
                action = "unloaded"
            elif command == "reload":
                action = "reloaded"
            elif command == "enable":
                action = "enabled"
            elif command == "disable":
                action = "disabled"
            output.cmdPRIVMSG(source, "Module(s) successfully {}: {}".format(action, ", ".join(success)))
            if command == "load" or command == "unload" or command == "reload":
                data.clear()
        for fail in failed:
            output.cmdPRIVMSG(source, fail)

moduleCommands = ModuleLoaderCommands()

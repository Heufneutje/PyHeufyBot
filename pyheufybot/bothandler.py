import os, subprocess
from twisted.internet import reactor, threads
from heufybot import HeufyBotFactory
from pyheufybot.logger import log
from config import Config

class BotHandler(object):
    def __init__(self):
        self.factories = {}
        self.configs = []
        self.globalConfig = None
        self.configFile = None

    def loadConfigs(self, configFile):
        self.configFile = configFile
        log("[BotHandler] --- Loading configs...", None)
        self.globalConfig = Config(configFile, None)

        if not self.globalConfig.loadConfig():
            return

        configList = self.getConfigList()
        if len(configList) == 0:
            log("[BotHandler] WARNING: No server configs found. Using the global config instead.", None)
            self.startFactory(self.globalConfig)
        else:
            for filename in configList:
                config = Config(filename, self.globalConfig.settings)
                config.loadConfig()
                self.configs.append(config)
                self.startFactory(config)
        reactor.run()

    def startFactory(self, config):
        server = config.getSettingWithDefault("server", "irc.foo.bar")
        port = config.getSettingWithDefault("port", 6667)
        if server in self.factories:
            log("[BotHandler] WARNING: Can't join server {} because it is already in the server list!".format(server), None)
            return False
        else:
            log("[BotHandler] --- Initiating a connection to {}...".format(server), None)
            factory = HeufyBotFactory(config, self)
            self.factories[server] = factory
            reactor.connectTCP(server, port, factory)
            return True

    def stopFactory(self, server, quitMessage=None, reconnect=False):
        if server in self.factories:
            factory = self.factories[server]
            log("[BotHandler] --- {} connection to {}...".format("Restarting" if reconnect else "Closing" ,server), None)
            if not quitMessage:
                if reconnect:
                    quitMessage = "Reconnecting..."
                else:
                    quitMessage = "Disconnecting..."

            factory.shouldReconnect = reconnect
            factory.bot.quit(quitMessage)
            if not reconnect:
                del self.factories[server]

            if len(self.factories) == 0:
                log("[BotHandler] --- No more open connections found; stopping reactor...", None)
                reactor.callLater(3.0, reactor.stop)

            return True
        else:
            return False

    def quit(self, quitMessage=None, restart=False):
        if not quitMessage:
            if restart:
                quitMessage = "Restarting..."
            else:
                quitMessage = "Shutting down..."
        servers = self.factories.keys()
        for factoryName in servers:
            self.stopFactory(factoryName, quitMessage, False)
        if restart:
            threads.deferToThread(self.fullRestart)

    def fullRestart(self):
        log("[BotHandler] Restarting...", None)
        reactor.callLater(3.0, subprocess.call("python app.py"))
        # reactor.callLater(3.0, os.execl, sys.executable, sys.executable, *sys.argv)

    def getConfigList(self):
        root = os.path.join("config")
        configs = []

        for item in os.listdir(root):
            if not os.path.isfile(os.path.join(root, item)):
                continue
            if not item.endswith(".yml"):
                continue
            if item == self.configFile:
                continue

            configs.append(item)

        return configs

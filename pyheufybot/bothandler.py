import os
from twisted.internet import reactor
from heufybot import HeufyBotFactory
from pyheufybot.logger import log
from config import Config

class BotHandler(object):
    _instance = None

    def __init__(self):
        self.factories = {}
        self.globalConfig = None
        self.configFile = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BotHandler, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

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
            factory = HeufyBotFactory(config)
            self.factories[server] = factory
            reactor.connectTCP(server, port, factory)
            return True

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

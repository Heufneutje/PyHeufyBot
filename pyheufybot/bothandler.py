import os
from twisted.internet import reactor
from heufybot import HeufyBot, HeufyBotFactory
from config import Config

class BotHandler(object):
    factories = {}
    globalConfig = None    

    def __init__(self, configFile):
        print "--- Loading configs..."
        self.configFile = configFile
        self.globalConfig = Config(configFile, None)
        
        if not self.globalConfig.loadConfig():
            return

        configList = self.getConfigList()
        if len(configList) == 0:
            print "*** WARNING: No server configs found. Using the global config instead."
            self.startFactory(globalConfig)
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
            print "*** WARNING: Can't join server {} because it is already in the server list!".format(server)
            return False
        else:
            print "--- Initiating a connection to {}...".format(server)
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

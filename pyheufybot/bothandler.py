import os
from twisted.internet import reactor
from heufybot import HeufyBot, HeufyBotFactory
from config import Config

class BotHandler(object):
    factories = {}
    globalConfig = None

    def __init__(self):
        print "--- Loading configs..."
        self.globalConfig = Config("globalconfig.yml")
        
        if not self.globalConfig.loadConfig(None):  
            return

        configList = self.getConfigList()
        if len(configList) == 0:
            print "WARNING: No server configs found. Using the global config instead."
        else:
            for filename in self.getConfigList():
                config = Config(filename, globalConfig.settings)

    def getConfigList(self):
        root = os.path.join("config")
        configs = []

        for item in os.listdir(root):
            if not os.path.isfile(os.path.join(root, item)):
                continue
            if not item.endswith(".yml"):
                continue
            if item == "globalconfig.yml":
                continue

            configs.append(item)

        return configs

if __name__ == "__main__":
    # Create folders
    if not os.path.exists(os.path.join("config")):
        os.makedirs("config")

    handler = BotHandler()

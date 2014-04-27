import os
from twisted.internet import reactor
from heufybot import HeufyBot, HeufyBotFactory
from config import Config

class BotHandler(object):
    factories = {}
    globalConfig = None

    def __init__(self):
        self.globalConfig = Config("globalconfig.yml")
        self.globalConfig.loadConfig(None)

if __name__ == "__main__":
    # Create folders
    if not os.path.exists(os.path.join("config")):
        os.makedirs("config")

    handler = BotHandler()
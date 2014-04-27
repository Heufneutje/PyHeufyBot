import os
from twisted.internet import reactor
from heufybot import HeufyBot, HeufyBotFactory

class BotHandler(object):
    factories = {}
    globalSettings = {}

    def __init__(self):
        pass

if __name__ == "__main__":
    # Create folders
    if not os.path.exists(os.path.join("config")):
        os.makedirs("config")

    handler = BotHandler()
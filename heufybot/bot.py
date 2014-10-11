from twisted.internet import reactor
from heufybot.config import Config
from heufybot.factory import HeufyBotFactory


class HeufyBot(object):
    def __init__(self, configFile):
        self.config = Config(configFile)
        self.config.readConfig()
        self.connectionFactory = HeufyBotFactory(self)
        reactor.connectTCP("heufneutje.net", 6667, self.connectionFactory)
        reactor.run()

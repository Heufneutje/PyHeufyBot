from twisted.internet import reactor
from heufybot.config import Config
from heufybot.factory import HeufyBotFactory
from heufybot.utils.logutils import LevelLoggingObserver


class HeufyBot(object):
    def __init__(self):
        self.config = Config("heufybot.yaml")
        self.config.readConfig()
        self.connectionFactory = HeufyBotFactory(self)
        observer = LevelLoggingObserver(open("test.log", "a"), 1)
        observer.start()
        reactor.connectTCP("heufneutje.net", 6667, self.connectionFactory)
        reactor.run()

heufybot = HeufyBot()

from twisted.internet import reactor
from heufybot.utils.logutils import LevelLoggingObserver
from factory import HeufyBotFactory


class HeufyBot(object):
    def __init__(self):
        self.connectionFactory = HeufyBotFactory(self)
        observer = LevelLoggingObserver(open("test.log", "a"), 1)
        observer.start()
        reactor.connectTCP("heufneutje.net", 6667, self.connectionFactory)
        reactor.run()

heufybot = HeufyBot()

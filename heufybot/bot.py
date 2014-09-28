from twisted.internet import reactor
from factory import HeufyBotFactory


class HeufyBot(object):
    def __init__(self):
        self.connectionFactory = HeufyBotFactory(self)
        reactor.connectTCP("heufneutje.net", 6667, self.connectionFactory)
        reactor.run()

heufybot = HeufyBot()
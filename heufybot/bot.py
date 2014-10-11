from twisted.internet import reactor
from twisted.python import log
from heufybot.config import Config
from heufybot.factory import HeufyBotFactory
import logging


class HeufyBot(object):
    def __init__(self, configFile):
        self.config = Config(configFile)
        self.connectionFactory = HeufyBotFactory(self)
        self.servers = {}
        self.startup()

    def startup(self):
        log.msg("Loading configuration file...")
        self.config.readConfig()
        # TODO: Load modules here
        log.msg("Initiating connections...")
        self._initiateConnections()
        log.msg("Starting reactor...")
        reactor.run()

    def _initiateConnections(self):
        for server in self.config["servers"].iterkeys():
            self.connectServer(server)

    def connectServer(self, host):
        if host in self.servers:
            error = "A connection to {} was requested, but already exists.".format(host)
            log.msg(error, level=logging.WARNING)
            return error
        if host not in self.config["servers"]:
            error = "A connection to {} was requested, but there is no config data for this server.".format(host)
            log.msg(error, level=logging.WARNING)
            return error
        port = int(self.config.serverItemWithDefault(host, "port", 6667))
        log.msg("Attempting connection to {}/{}...".format(host, port))
        reactor.connectTCP(host, port, self.connectionFactory)

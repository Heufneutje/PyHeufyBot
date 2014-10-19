from twisted.internet import reactor
from twisted.python import log
from heufybot.config import Config
from heufybot.factory import HeufyBotFactory
from heufybot.modulehandler import ModuleHandler
import logging

# Try to enable SSL support
try:
    from twisted.internet import ssl
    sslSupported = True
except ImportError:
    sslSupported = False


class HeufyBot(object):
    def __init__(self, configFile):
        self.config = Config(configFile)
        self.connectionFactory = HeufyBotFactory(self)
        self.moduleHandler = ModuleHandler(self)
        self.servers = {}
        self.startup()

    def startup(self):
        if not sslSupported:
            log.msg("The PyOpenSSL package was not found. You will not be able to connect to servers using SSL.",
                    level=logging.WARNING)
        log.msg("Loading configuration file...")
        self.config.readConfig()
        log.msg("Loading modules...")
        self.moduleHandler.loadAllModules()
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
        if self.config.serverItemWithDefault(host, "ssl", False):
            log.msg("Attempting secure connection to {}/{}...".format(host, port))
            if sslSupported:
                reactor.connectSSL(host, port, self.connectionFactory, ssl.ClientContextFactory())
            else:
                log.msg("Can't connect to {}/{}; PyOpenSSL is required to allow secure connections.".
                        format(host, port), level=logging.ERROR)
        else:
            log.msg("Attempting connection to {}/{}...".format(host, port))
            reactor.connectTCP(host, port, self.connectionFactory)

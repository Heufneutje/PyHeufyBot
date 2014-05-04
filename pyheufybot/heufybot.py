from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from pyheufybot.globalvars import version
from pyheufybot.config import Config
from pyheufybot.user import IRCUser
from pyheufybot.channel import IRCChannel
from pyheufybot.message import IRCMessage
from pyheufybot.logger import log

class HeufyBot(irc.IRCClient):
    def __init__(self, factory):
        self.factory = factory
        self.usermodes = {}
        self.channels = {}

    def connectionMade(self):
        self.nickname = self.factory.config.settings["nickname"]
        self.username = self.factory.config.settings["username"]
        self.realname = self.factory.config.settings["realname"]
        irc.IRCClient.connectionMade(self)
        
        log("--- Connected to {}.".format(self.factory.config.getSettingWithDefault("server", "irc.foo.bar")), None)
        log("--- Resetting reconnection delay...", None)
        self.factory.resetDelay()

    def signedOn(self):
        autojoinChannels = self.factory.config.getSettingWithDefault("channels", [])
        for channel in autojoinChannels:
            self.join(channel)

    def irc_JOIN(self, prefix, params):
        user = self.getUser(prefix[:prefix.index("!")])
        if not user:
            user = IRCUser(prefix)

        channel = self.getChannel(params[0])

        if user.nickname == self.nickname:
            # The bot is joining the channel, do setup
            channel = IRCChannel(params[0])
            self.channels[params[0]] = channel

            self.sendLine("WHO {}".format(channel.name))
            self.sendLine("MODE {}".format(channel.name))
        else:
            # Someone else is joining the channel, add them to that channel's user dictionary
            channel.users[user.nickname] = user

        message = IRCMessage("JOIN", user, channel, "")
        log(">> {} ({}@{}) has joined {}".format(user.nickname, user.username, user.hostname, channel.name), channel.name)

    def irc_PART(self, prefix, params):
        user = self.getUser(prefix[:prefix.index("!")])
        channel = self.getChannel(params[0])

        partMessage = ""
        if len(params) > 1:
            partMessage = params[1]

        if user.nickname == self.nickname:
            # The bot is leaving the channel
            del self.channels[channel.name]
        else:
            # Someone else is leaving the channel
            del channel.users[user.nickname]

        message = IRCMessage("PART", user, channel, partMessage)
        log("<< {} ({}@{}) has left {} ({})".format(user.nickname, user.username, user.hostname, channel.name, partMessage), channel.name)

    def getChannel(self, name):
        if name in self.channels:
            return self.channels[name]
        else:
            return None

    def getUser(self, nickname):
        for channel in self.channels.values():
            if nickname in channel.users:
                return channel.users[nickname]
        return None

class HeufyBotFactory(protocol.ReconnectingClientFactory):
    protocol = HeufyBot
    
    def __init__(self, config):
        self.config = config

    def startedConnecting(self, connector):
        log("--- Connecting to server {}...".format(self.config.getSettingWithDefault("server", "irc.foo.bar")), None)

    def buildProtocol(self, addr):
        self.bot = HeufyBot(self)
        return self.bot

    def clientConnectionLost(self, connector, reason):
        log("*** Connection lost. (Reason: {})".format(reason), None)
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        log("*** Connection failed. (Reason: {})".format(reason), None)
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
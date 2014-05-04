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

    def privmsg(self, user, channel, msg):
        messageChannel = self.getChannel(channel)
        messageUser = self.getUser(user[:user.index("!")])

        if not messageUser:
            # If this is a PM, the bot will have no knowledge of the user. Create a temporary one just for this message
            messageUser = IRCUser(user)

        message = IRCMessage("PRIVMSG", messageUser, messageChannel, msg)

        if not message.replyTo == messageUser.nickname:
            # Don't log PMs
            # TODO: Make logging PMs a setting
            # TODO: Add the user's status symbol as a prefix
            log("<{}{}> {}".format("", messageUser.nickname, msg), message.replyTo)

    def action(self, user, channel, msg):
        messageChannel = self.getChannel(channel)
        messageUser = self.getUser(user[:user.index("!")])

        if not messageUser:
            # If this is a PM, the bot will have no knowledge of the user. Create a temporary one just for this message
            messageUser = IRCUser(user)

        message = IRCMessage("ACTION", messageUser, messageChannel, msg)

        if not message.replyTo == messageUser.nickname:
            # Don't log PMs
            # TODO: Make logging PMs a setting
            log("* {} {}".format(messageUser.nickname, msg), message.replyTo)

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
            if user.nickname in channel.users:
                # This will trigger if a desync ever happens. Send WHO to fix it.
                channel.users = {}
                self.sendLine("WHO {}".format(channel.name))
            else:
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
            if user.nickname not in channel.users:
                # This will trigger if a desync ever happens. Send WHO to fix it.
                channel.users = {}
                self.sendLine("WHO {}".format(channel.name))
            else:
                del channel.users[user.nickname]

        message = IRCMessage("PART", user, channel, partMessage)
        log("<< {} ({}@{}) has left {} ({})".format(user.nickname, user.username, user.hostname, channel.name, partMessage), channel.name)

    def irc_QUIT(self, prefix, params): 
        user = self.getUser(prefix[:prefix.index("!")])

        quitMessage = ""
        if len(params) > 0:
            quitMessage = params[0]

        for channel in self.channels.itervalues():
            if user.nickname in channel.users:
                log("<< {} ({}@{}) has quit IRC ({})".format(user.nickname, user.username, user.hostname, quitMessage), channel.name)
                del channel.users[user.nickname]

        message = IRCMessage("QUIT", user, None, quitMessage)

    def irc_KICK(self, prefix, params):
        user = self.getUser(prefix[:prefix.index("!")])
        channel = self.getChannel(params[0])
        
        kickee = params[1]
        kickMessage = ""
        if len(params) > 2:
            kickMessage = params[2]

        if kickee == self.nickname:
            # The bot is kicked from the channel
            del self.channels[channel.name]
        else:
            # Someone else is kicking someone from the channel
            del channel.users[kickee]

        message = IRCMessage("KICK", user, channel, kickMessage)
        log("-- {} was kicked from {} by {} ({})".format(kickee, channel.name, user.nickname, kickMessage), channel.name)

    def irc_NICK(self, prefix, params):
        user = self.getUser(prefix[:prefix.index("!")])

        oldnick = user.nickname
        newnick = params[0]

        for channel in self.channels.itervalues():
            if oldnick in channel.users:
                channel.users[newnick] = user
                del channel.users[oldnick]
                log("-- {} is now known as {}".format(oldnick, newnick), channel.name)

        message = IRCMessage("NICK", user, None, oldnick)
        user.nickname = newnick

    def nickChanged(self, nick):
        self.nickname = nick

    def irc_RPL_WHOREPLY(self, prefix, params):
        user = self.getUser(params[5])
        if not user:
            user = IRCUser("{}!{}@{}".format(params[5], params[2], params[3]))
        else:
            user.username = params[2]
            user.hostname = params[3]
        channel = self.channels[params[1]]
        channel.users[user.nickname] = user
        # TODO: Parse flags and other WHO reply information

    '''
    # Will do this later since NAMES prefixes nicknames with their status and the bot doesn't know statuses yet
    def irc_RPL_NAMREPLY(self, prefix, params):
        channelUsers = params[3].strip().split(" ")
        for channelUser in channelUsers:
            user = self.getUser(channelUser)
            if not user:
                user = IRCUser("{}!{}@{}".format(channelUser, None, None))
            channel = self.channels[params[2]]
            channel.users[user.nickname] = user
    '''

    def getChannel(self, name):
        if name in self.channels:
            return self.channels[name]
        else:
            return None

    def getUser(self, nickname):
        for channel in self.channels.itervalues():
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
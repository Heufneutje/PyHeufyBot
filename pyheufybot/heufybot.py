import datetime, time
from twisted.words.protocols import irc
from twisted.internet import protocol
from pyheufybot.user import IRCUser
from pyheufybot.channel import IRCChannel
from pyheufybot.message import IRCMessage
from pyheufybot.logger import log
from pyheufybot.serverinfo import ModeType, ServerInfo
from pyheufybot.module_interface import ModuleInterface

class HeufyBot(irc.IRCClient):
    def __init__(self, factory):
        self.factory = factory
        self.usermodes = {}
        self.channels = {}
        self.serverInfo = ServerInfo()
        self.serverInfo.address = factory.config.getSettingWithDefault("server", "irc.foo.bar")
        self.moduleInterface = ModuleInterface(self)

    def connectionMade(self):
        self.nickname = self.factory.config.getSettingWithDefault("nickname", "PyHeufyBot")
        self.username = self.factory.config.getSettingWithDefault("username", "PyHeufyBot")
        self.realname = self.factory.config.getSettingWithDefault("realname", "PyHeufyBot")
        if self.factory.config.getSettingWithDefault("passwordType", None) == "ServerPass":
            self.password = self.factory.config.getSettingWithDefault("password", "")
        irc.IRCClient.connectionMade(self)
        
        log("--- Connected to {}.".format(self.factory.config.getSettingWithDefault("server", "irc.foo.bar")), None)
        log("--- Resetting reconnection delay...", None)
        self.factory.resetDelay()

    def signedOn(self):
        autojoinChannels = self.factory.config.getSettingWithDefault("channels", [])
        for channel in autojoinChannels:
            self.join(channel)

        message = IRCMessage("USER", None, None, "")
        self.moduleInterface.handleMessage(message)

    def msg(self, user, message, length=None):
        messageUser = self.getUser(self.nickname)
        if not messageUser:
            messageUser = IRCUser("{}!{}@{}".format(self.nickname, None, None))
        messageChannel = user if user in self.channels else None

        message = IRCMessage("PRIVMSG", messageUser, messageChannel, message)
        self.moduleInterface.handleMessage(message)

        irc.IRCClient.msg(self, user, message, length)

    def privmsg(self, user, channel, msg):
        messageChannel = self.getChannel(channel)
        messageUser = self.getUser(user[:user.index("!")])

        if not messageUser:
            # If this is a PM, the bot will have no knowledge of the user. Create a temporary one just for this message
            messageUser = IRCUser(user)

        message = IRCMessage("PRIVMSG", messageUser, messageChannel, msg)
        self.moduleInterface.handleMessage(message)

        if not message.replyTo == messageUser.nickname:
            # Don't log PMs
            # TODO: Make logging PMs a setting
            if messageChannel.ranks[messageUser.nickname] != "":
                statusChar = self.serverInfo.prefixesModeToChar[messageChannel.getHighestRankOfUser(messageUser.nickname, self.serverInfo.prefixOrder)]
            else:
                statusChar = ""
            log("<{}{}> {}".format(statusChar, messageUser.nickname, msg), message.replyTo)

    def action(self, user, channel, msg):
        messageChannel = self.getChannel(channel)
        messageUser = self.getUser(user[:user.index("!")])

        if not messageUser:
            # If this is a PM, the bot will have no knowledge of the user. Create a temporary one just for this message
            messageUser = IRCUser(user)

        message = IRCMessage("ACTION", messageUser, messageChannel, msg)
        self.moduleInterface.handleMessage(message)

        if not message.replyTo == messageUser.nickname:
            # Don't log PMs
            # TODO: Make logging PMs a setting
            log("* {} {}".format(messageUser.nickname, msg), message.replyTo)

    def irc_JOIN(self, prefix, params):
        user = self.getUser(prefix[:prefix.index("!")])
        if not user:
            user = IRCUser(prefix)
        else:
            exclamationIndex = prefix.index("!")
            atIndex = prefix.index("@")
            user.username = prefix[exclamationIndex + 1:atIndex]
            user.hostname = prefix[atIndex + 1:]

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
                # This will trigger if a desync ever happens. Send NAMES and WHO to fix it.
                self.fixChannelListDesync(channel)
            else:
                channel.users[user.nickname] = user
                channel.ranks[user.nickname] = ""

        message = IRCMessage("JOIN", user, channel, "")
        self.moduleInterface.handleMessage(message)
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
                # This will trigger if a desync ever happens. Send NAMES and WHO to fix it.
                self.fixChannelListDesync(channel)
            else:
                del channel.users[user.nickname]
                del channel.ranks[user.nickname]

        message = IRCMessage("PART", user, channel, partMessage)
        self.moduleInterface.handleMessage(message)
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
                del channel.ranks[user.nickname]

        message = IRCMessage("QUIT", user, None, quitMessage)
        self.moduleInterface.handleMessage(message)

    def irc_KICK(self, prefix, params):
        user = self.getUser(prefix[:prefix.index("!")])
        channel = self.getChannel(params[0])
        kickee = params[1]
        kickMessage = ""

        if user.nickname not in channel.users or kickee not in channel.users:
            self.fixChannelListDesync(channel)
        else:
            if len(params) > 2:
                kickMessage = params[2]
    
            if kickee == self.nickname:
                # The bot is kicked from the channel
                del self.channels[channel.name]
            else:
                # Someone else is kicking someone from the channel
                del channel.users[kickee]
                del channel.ranks[kickee]

        message = IRCMessage("KICK", user, channel, kickMessage)
        self.moduleInterface.handleMessage(message)
        log("-- {} was kicked from {} by {} ({})".format(kickee, channel.name, user.nickname, kickMessage), channel.name)

    def irc_NICK(self, prefix, params):
        user = self.getUser(prefix[:prefix.index("!")])

        oldnick = user.nickname
        newnick = params[0]

        for channel in self.channels.itervalues():
            if oldnick in channel.users:
                channel.users[newnick] = user
                del channel.users[oldnick]
                channel.ranks[newnick] = channel.ranks[oldnick]
                del channel.ranks[oldnick]

                log("-- {} is now known as {}".format(oldnick, newnick), channel.name)

        user.nickname = newnick
        message = IRCMessage("NICK", user, None, oldnick)
        self.moduleInterface.handleMessage(message)

    def modeChanged(self, user, channel, set, modes, args):
        modeUser = self.getUser(user)
        modeChannel = self.getChannel(channel)

        if not modeUser:
            # The user is unknown. This is probably setting a usermode or a service. Create a temporary user.
            if "!" in user:
                modeUser = IRCUser(user)
            else:
                # User doesn't have a username or hostname.
                modeUser = IRCUser("{}!{}@{}".format(user, None, None))

        if not modeChannel:
            # Setting a usermode
            for mode, arg in zip(modes, args):
                if set:
                    self.usermodes[mode] = arg
                else:
                    del self.usermodes[mode]
        else:
            # Setting a chanmode
            for mode, arg in zip(modes, args):
                if mode in self.serverInfo.prefixesModeToChar:
                    # Setting a status mode
                    if set:
                        modeChannel.ranks[arg] = modeChannel.ranks[arg] + mode
                    else:
                        modeChannel.ranks[arg] = modeChannel.ranks[arg].replace(mode, "")
                else:
                    # Setting a normal chanmode
                    if set:
                        modeChannel.modes[mode] = arg
                    else:
                        del modeChannel.modes[mode]

        logArgs = [arg for arg in args if arg is not None]
        operator = '+' if set else '-'
        target = modeChannel.name if modeChannel else None

        log("-- {} sets mode: {}{} {}".format(modeUser.nickname, operator, modes, " ".join(logArgs)), target)

    def irc_TOPIC(self, prefix, params):
        user = self.getUser(prefix[:prefix.index("!")])
        channel = self.getChannel(params[1])
        channel.topic = params[2]
        channel.topicSetter = user.getFullName()
        channel.topicTimestamp = time.time()

        log("-- {} changes topic to \"{}\"".format(user.nickname, channel.topic), channel.name)

    def irc_RPL_TOPIC(self, prefix, params):
        channel = self.getChannel(params[1])
        channel.topic = params[2]

        log("-- Topic is \"{}\"".format(channel.topic), channel.name)

    def irc_unknown(self, prefix, command, params):
        if command == "333":
            # RPL_TOPICWHOTIME: This is in the RFC but not implemented. Tsk tsk, Twisted.
            channel = self.getChannel(params[1])
            channel.topicSetter = params[2]
            channel.topicTimestamp = long(params[3])
            log("-- Topic set by {} on {}".format(params[2], datetime.datetime.fromtimestamp(channel.topicTimestamp)), channel.name)
        elif command == "329":
            # RPL_CREATIONTIME: Not RFC, but still used pretty much anywhere
            channel = self.getChannel(params[1])
            channel.creationTime = long(params[2])
            log("-- Channel was created on {}".format(datetime.datetime.fromtimestamp(channel.creationTime)), channel.name)

    def irc_RPL_NAMREPLY(self, prefix, params):
        channel = self.getChannel(params[2])

        # Rebuild the list if it is complete
        if channel.namesListComplete:
            channel.namesListComplete = False
            channel.users.clear()
            channel.ranks.clear()

        channelUsers = params[3].strip().split(" ")
        for channelUser in channelUsers:
            rank = ""

            if channelUser[0] in self.serverInfo.prefixesCharToMode:
                rank = self.serverInfo.prefixesCharToMode[channelUser[0]]
                channelUser = channelUser[1:]

            user = self.getUser(channelUser)
            if not user:
                user = IRCUser("{}!{}@{}".format(channelUser, None, None))

            channel.users[user.nickname] = user
            channel.ranks[user.nickname] = rank

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        # The NAMES list is now complete
        channel = self.channels[params[1]]
        channel.namesListComplete = True

    def irc_RPL_WHOREPLY(self, prefix, params):
        channel = self.getChannel(params[1])
        user = channel.users[params[5]]

        if not user:
            user = IRCUser("{}!{}@{}".format(params[5], params[2], params[3]))
        else:
            user.username = params[2]
            user.hostname = params[3]
        
        user.server = params[4]
        user.hops, user.realname = params[7].split(" ", 1) #The RFC is weird.

        flags = params[6]
        statusFlags = None
        if flags[0] == "G":
            user.away = True
        if len(flags) > 1:
            if flags[1] == "*":
                user.oper = True
                statusFlags = flags[2:]
            else:
                statusFlags = flags[1:]
        statusModes = ""
        if statusFlags:
            del channel.ranks[user.nickname]
            for flag in statusFlags:
                statusModes = statusModes + self.serverInfo.prefixesCharToMode[flag]
        channel.ranks[user.nickname] = statusModes

    def irc_RPL_CHANNELMODEIS(self, prefix, params):
        channel = self.getChannel(params[1])
        modestring = params[2][1:]
        modeparams = params[3:]

        for mode in modestring:
            if self.serverInfo.chanModes[mode] == ModeType.PARAM_SET or self.serverInfo.chanModes[mode] == ModeType.PARAM_SETUNSET:
                # Mode takes an argument
                channel.modes[mode] = modeparams[0]
                del modeparams[0]
            else:
                channel.modes[mode] = None

        log("-- Channel modes set: {}".format(params[2]), channel.name)

    def irc_RPL_MYINFO(self, prefix, params):
        self.serverInfo.name = params[1]
        self.serverInfo.version = params[2]

        for mode in params[3]:
            if mode == "s":
                self.serverInfo.userModes[mode] = ModeType.LIST
            else:
                self.serverInfo.userModes[mode] = ModeType.NORMAL

    def isupport(self, options):
        for item in options:
            if "=" in item:
                option = item.split("=")
                if option[0] == "CHANTYPES":
                    self.serverInfo.chanTypes = option[1]
                elif option[0] == "CHANMODES":
                    modes = option[1].split(",")
                    for mode in modes[0]:
                        self.serverInfo.chanModes[mode] = ModeType.LIST
                    for mode in modes[1]:
                        self.serverInfo.chanModes[mode] = ModeType.PARAM_SETUNSET
                    for mode in modes[2]:
                        self.serverInfo.chanModes[mode] = ModeType.PARAM_SET
                    for mode in modes[3]:
                        self.serverInfo.chanModes[mode] = ModeType.NORMAL
                elif option[0] == "NETWORK":
                    self.serverInfo.network = option[1]
                elif option[0] == "PREFIX":
                    prefixes = option[1]
                    statusModes = prefixes[:prefixes.find(')')]
                    statusChars = prefixes[prefixes.find(')'):]
                    self.serverInfo.prefixOrder = statusModes
                    for i in range(1, len(statusModes)):
                        self.serverInfo.prefixesModeToChar[statusModes[i]] = statusChars[i]
                        self.serverInfo.prefixesCharToMode[statusChars[i]] = statusModes[i]

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
    
    def fixChannelListDesync(self, channel):
        channel.users = {}
        channel.ranks = {}
        self.sendLine("NAMES {}".format(channel.name))
        self.sendLine("WHO {}".format(channel.name))

class HeufyBotFactory(protocol.ReconnectingClientFactory):
    protocol = HeufyBot
    
    def __init__(self, config):
        self.config = config

    def startedConnecting(self, connector):
        log("--- Connecting to server {}...".format(self.config.getSettingWithDefault("server", "irc.foo.bar")), None)

    def buildProtocol(self, addr):
        self.bot = HeufyBot(self)
        self.bot.moduleInterface.loadAllModules()
        return self.bot

    def clientConnectionLost(self, connector, reason):
        log("*** Connection lost. (Reason: {})".format(reason), None)
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        log("*** Connection failed. (Reason: {})".format(reason), None)
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

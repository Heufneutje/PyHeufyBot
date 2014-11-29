from twisted.words.protocols import irc
from heufybot.channel import IRCChannel
from heufybot.user import IRCUser
from heufybot.utils import ModeType, parseUserPrefix, timeutils
import logging


class InputHandler(object):
    def __init__(self, connection):
        self.connection = connection

    def handleCommand(self, command, prefix, params):
        parsedPrefix = parseUserPrefix(prefix)
        nick = parsedPrefix[0]
        ident = parsedPrefix[1]
        host = parsedPrefix[2]
        moduleHandler = self.connection.bot.moduleHandler

        if command == "INVITE":
            if nick in self.connection.users:
                inviter = self.connection.users[nick]
            else:
                inviter = IRCUser(nick, ident, host)
            self.connection.bot.moduleHandler.runGenericAction("channelinvite", params[1], inviter)
            self.connection.outputHandler.cmdJOIN(params[1])

        elif command == "JOIN":
            if nick not in self.connection.users:
                user = IRCUser(nick, ident, host)
                self.connection.users[nick] = user
            else:
                user = self.connection.users[nick]
            if params[0] not in self.connection.channels:
                channel = IRCChannel(params[0])
                self.connection.outputHandler.cmdWHO(params[0])
                self.connection.channels[params[0]] = channel
            else:
                channel = self.connection.channels[params[0]]
            channel.users[nick] = user
            channel.ranks[nick] = ""
            moduleHandler.runGenericAction("channeljoin", self.connection.name, channel, user)

        elif command == "KICK":
            if params[0] not in self.connection.channels:
                self.connection.log("Received KICK message for unknown channel {}.".format(params[0]),
                                    level=logging.WARNING)
                return
            channel = self.connection.channels[params[0]]
            if params[1] not in channel.users:
                self.connection.log("Received KICK message for unknown user {} in channel {}.".format(nick, params[0]),
                                    level=logging.WARNING)
                return
            if nick not in self.connection.users:
                # Technically opers could KICK a user despite not being in the channel themselves
                kicker = IRCUser(nick, ident, host)
            else:
                kicker = self.connection.users[nick]
            kicked = self.connection.users[params[1]]
            reason = ""
            if len(params) > 2:
                reason = params[2]
            # We need to run the action before we actually get rid of the user
            moduleHandler.runGenericAction("channelkick", self.connection.name, channel, kicker, kicked, reason)
            if kicked.nick == self.connection.nick:
                del self.connection.channels[params[0]]
            else:
                del channel.users[kicked]
                del channel.ranks[kicked]

        elif command == "NICK":
            if nick not in self.connection.users:
                self.connection.log("Received NICK message for unknown user {}.".format(nick), level=logging.WARNING)
                return
            user = self.connection.users[nick]
            newNick = params[0]
            user.nick = newNick
            self.connection.users[newNick] = user
            del self.connection.users[nick]
            for channel in self.connection.channels.itervalues():
                if nick in channel.users:
                    channel.users[newNick] = user
                    channel.ranks[newNick] = channel.ranks[nick]
                    del channel.users[nick]
                    del channel.ranks[nick]
            if nick == self.connection.nick:
                self.connection.nick = newNick
            moduleHandler.runGenericAction("changenick", self.connection.name, user, nick, newNick)

        elif command == "NOTICE":
            user = None
            if params[0][0] in self.connection.supportHelper.chanTypes:
                if params[0] in self.connection.channels:
                    source = self.connection.channels[params[0]]
                else:
                    # We got a notice for an unknown channel. Create a temporary IRCChannel object for it.
                    source = IRCChannel(params[0])
                if nick in self.connection.users:
                    user = self.connection.users[nick]
                else:
                    user = IRCUser(nick, ident, host)
            elif nick in self.connection.users:
                source = self.connection.users[nick]
            else:
                # We got a notice from an unknown user. Create a temporary IRCUser object for them.
                source = IRCUser(nick, ident, host)
            if isinstance(source, IRCChannel):
                moduleHandler.runGenericAction("notice-channel", self.connection, source, user, params[1])
            else:
                moduleHandler.runGenericAction("notice-user", self.connection, source, params[1])

        elif command == "PART":
            if params[0] not in self.connection.channels:
                self.connection.log("Received PART message for unknown channel {}.".format(params[0]),
                                    level=logging.WARNING)
                return
            channel = self.connection.channels[params[0]]
            if nick not in channel.users:
                self.connection.log("Received PART message for unknown user {} in channel {}.".format(nick, params[0]),
                                    level=logging.WARNING)
                return
            reason = ""
            if len(params) > 1:
                reason = params[1]
            user = self.connection.users[nick]
            # We need to run the action before we actually get rid of the user
            moduleHandler.runGenericAction("channelpart", self.connection.name, channel, user, reason)
            if nick == self.connection.nick:
                del self.connection.channels[params[0]]
            else:
                del channel.users[nick]
                del channel.ranks[nick]

        elif command == "PING":
            self.connection.outputHandler.cmdPONG(" ".join(params))

        elif command == "PRIVMSG":
            user = None
            if params[0][0] in self.connection.supportHelper.chanTypes:
                if params[0] in self.connection.channels:
                    source = self.connection.channels[params[0]]
                else:
                    # We got a message for an unknown channel. Create a temporary IRCChannel object for it.
                    source = IRCChannel(params[0])
                if nick in self.connection.users:
                    user = self.connection.users[nick]
                else:
                    user = IRCUser(nick, ident, host)
            elif nick in self.connection.users:
                source = self.connection.users[nick]
            else:
                # We got a message from an unknown user. Create a temporary IRCUser object for them.
                source = IRCUser(nick, ident, host)
            if params[1][0] == "\x01":
                message = params[1][1:len(params[1]) - 1]
                moduleHandler.runGenericAction("ctcp-message", self.connection.name, source, message)
            elif isinstance(source, IRCChannel):
                moduleHandler.runGenericAction("message-channel", self.connection, source, user, params[1])
            else:
                moduleHandler.runGenericAction("message-user", self.connection, source, params[1])

        elif command == "TOPIC":
            if params[0] not in self.connection.channels:
                self.connection.log("Received TOPIC message for unknown channel {}.".format(params[0]),
                                    level=logging.WARNING)
                return
            channel = self.connection.channels[params[0]]
            if nick not in self.connection.users:
                # A user that's not in the channel can change the topic so let's make a temporary user.
                user = IRCUser(nick, ident, host)
            else:
                user = self.connection.users[nick]
            oldTopic = channel.topic
            channel.topic = params[1]
            channel.topicSetter = user.fullUserPrefix()
            channel.topicTimestamp = timeutils.timestamp(timeutils.now())
            moduleHandler.runGenericAction("changetopic", self.connection.name, channel, oldTopic, params[1])

        elif command == "QUIT":
            if nick not in self.connection.users:
                self.connection.log("Received a QUIT message for unknown user {}.".format(nick), level=logging.WARNING)
                return
            reason = ""
            if len(params) > 0:
                reason = params[0]
            user = self.connection.users[nick]
            moduleHandler.runGenericAction("userquit", self.connection.name, user, reason)
            for channel in self.connection.channels.itervalues():
                if nick in channel.users:
                    del channel.users[nick]
                    del channel.ranks[nick]

    def handleNumeric(self, numeric, prefix, params):
        if numeric == irc.RPL_WELCOME:
            self.connection.loggedIn = True
            self.connection.bot.moduleHandler.runGenericAction("welcome", self.connection.name)
            channels = self.connection.bot.config.serverItemWithDefault(self.connection.name, "channels", {})
            for channel, key in channels.iteritems():
                self.connection.outputHandler.cmdJOIN(channel, key if key else "")

        elif numeric == irc.RPL_MYINFO:
            self.connection.supportHelper.serverName = params[1]
            self.connection.supportHelper.serverVersion = params[2]
            self.connection.supportHelper.userModes = params[3]

        elif numeric == irc.RPL_ISUPPORT:
            tokens = {}
            # The first param is our prefix and the last one is ":are supported by this server"
            for param in params[1:len(params) - 1]:
                keyValuePair = param.split("=")
                if len(keyValuePair) > 1:
                    tokens[keyValuePair[0]] = keyValuePair[1]
                else:
                    tokens[keyValuePair[0]] = ""
            if "CHANTYPES" in tokens:
                self.connection.supportHelper.chanTypes = tokens["CHANTYPES"]
            if "CHANMODES" in tokens:
                self.connection.supportHelper.chanModes.clear()
                groups = tokens["CHANMODES"].split(",")
                for mode in groups[0]:
                    self.connection.supportHelper.chanModes[mode] = ModeType.LIST
                for mode in groups[1]:
                    self.connection.supportHelper.chanModes[mode] = ModeType.PARAM_UNSET
                for mode in groups[2]:
                    self.connection.supportHelper.chanModes[mode] = ModeType.PARAM_SET
                for mode in groups[3]:
                    self.connection.supportHelper.chanModes[mode] = ModeType.NO_PARAM
            if "NETWORK" in tokens:
                self.connection.supportHelper.network = tokens["NETWORK"]
            if "PREFIX" in tokens:
                self.connection.supportHelper.statusModes.clear()
                self.connection.supportHelper.statusSymbols.clear()
                modes = tokens["PREFIX"][1:tokens["PREFIX"].find(")")]
                symbols = tokens["PREFIX"][tokens["PREFIX"].find(")") + 1:]
                self.connection.supportHelper.statusOrder = modes
                for i in range(len(modes)):
                    self.connection.supportHelper.statusModes[modes[i]] = symbols[i]
                    self.connection.supportHelper.statusSymbols[symbols[i]] = modes[i]
            self.connection.supportHelper.rawTokens.update(tokens)

        elif numeric == irc.RPL_NAMREPLY:
            channel = self.connection.channels[params[2]]
            if channel.userlistComplete:
                channel.userlistComplete = False
                channel.users.clear()
                channel.ranks.clear()
            for userPrefix in params[3].split():
                parsedPrefix = parseUserPrefix(userPrefix)
                nick = parsedPrefix[0]
                ranks = ""
                while nick[0] in self.connection.supportHelper.statusSymbols:
                    ranks += self.connection.supportHelper.statusSymbols[nick[0]]
                    nick = nick[1:]
                if nick in self.connection.users:
                    user = self.connection.users[nick]
                    user.ident = parsedPrefix[1]
                    user.host = parsedPrefix[2]
                else:
                    user = IRCUser(nick, parsedPrefix[1], parsedPrefix[2])
                    self.connection.users[nick] = user
                channel.users[nick] = user
                channel.ranks[nick] = ranks

        elif numeric == irc.RPL_ENDOFNAMES:
            channel = self.connection.channels[params[1]]
            channel.userlistComplete = True

        elif numeric == irc.RPL_WHOREPLY:
            if params[5] not in self.connection.users:
                self.connection.log("Received WHO reply for unknown user {}.".format(params[5]),
                                    level=logging.WARNING)
                return
            user = self.connection.users[params[5]]
            user.ident = params[2]
            user.host = params[3]
            user.server = params[4]
            flags = list(params[6])
            if flags.pop(0) == "G":
                user.isAway = True
            if len(flags) > 0 and flags.pop(0) == "*":
                user.isOper = True
            if params[1] in self.connection.channels:
                channel = self.connection.channels[params[1]]
                channel.ranks[params[5]] = ""
                for status in flags:
                    channel.ranks[params[5]] += self.connection.supportHelper.statusSymbols[status]
            user.hops = int(params[7].split()[0])
            user.gecos = params[7].split()[1]

        elif numeric == irc.ERR_NICKNAMEINUSE:
            newNick = "{}_".format(self.connection.nick)
            self.connection.log("Nickname {} is in use, retrying with {} ...".format(self.connection.nick, newNick))
            self.connection.nick = newNick
            self.connection.outputHandler.cmdNICK(self.connection.nick)

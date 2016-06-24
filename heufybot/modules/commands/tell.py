from twisted.plugin import IPlugin
from heufybot.channel import IRCChannel
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import networkName
from heufybot.utils.timeutils import durationToTimedelta, now, strftimeWithTimezone, timeDeltaString
from zope.interface import implements
from datetime import datetime
from fnmatch import fnmatch
import re


class TellCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Tell"

    def triggers(self):
        return ["tell", "tellafter", "stells", "rtell"]

    def actions(self):
        return super(TellCommand, self).actions() + [
            ("message-channel", 1, self.checkChannelTells),
            ("message-user", 1, self.checkPMTells),
            ("ctcp-message", 1, self.checkActions) ]

    def load(self):
        self.help = "Commands: tell <user> <message>, tellafter <user> <duration> <message>, rtell <message>, " \
                    "stells | Tell the specified user a message the next time they speak, removes a message sent by " \
                    " you from the database or lists your pending messages."
        self.commandHelp = {
            "tell": "tell <user> <message> | Tell the given user(s) a message when they next speak.",
            "tellafter": "tellafter <user> <duration> <message> | Tells the given user(s) a message when they speak "
                         "after the given duration or on the given date.",
            "stells": "stells | List all tells sent by you that have not yet been received.",
            "rtell <message>": "Remove the earlier message sent by you that matches."
        }
        if "tells" not in self.bot.storage:
            self.bot.storage["tells"] = {}
        self.tells = self.bot.storage["tells"]

    def checkChannelTells(self, server, channel, user, messageBody):
        self._processTells(server, channel.name, user.nick)

    def checkPMTells(self, server, user, messageBody):
        self._processTells(server, user.nick, user.nick)

    def checkActions(self, server, source, user, body):
        if not body.upper().startswith("ACTION"):
            return
        if isinstance(source, IRCChannel):
            self._processTells(server, source.name, user.nick)
        else:
            self._processTells(server, source.nick, source.nick)

    def execute(self, server, source, command, params, data):
        if command == "tell" or command == "tellafter":
            if len(params) == 0 or len(params) == 1:
                self.replyPRIVMSG(server, source, "Tell who?")
                return
            elif len(params) == 1 and command == "tellafter":
                self.replyPRIVMSG(server, source, "Tell it when?")
                return
            elif len(params) == 1 or len(params) == 2 and command == "tellafter":
                self.replyPRIVMSG(server, source, "Tell {} what?".format(params[0]))
                return
            sentTells = []
            if command == "tellafter":
                try:
                    date = datetime.strptime(params[1], "%Y-%m-%d")
                except ValueError:
                    date = now() + durationToTimedelta(params[1])
            else:
                date = now()
            for recep in params[0].split("&"):
                if recep.lower() == self.bot.servers[server].nick.lower():
                    self.replyPRIVMSG(server, source, "Thanks for telling me that, {}.".format(data["user"].nick))
                    continue
                message = {
                    "to": recep.lower(),
                    "body": " ".join(params[1:]) if command == "tell" else " ".join(params[2:]),
                    "date": now(),
                    "datetoreceive": date,
                    "from": data["user"].nick,
                    "source": source if source[0] in self.bot.servers[server].supportHelper.chanTypes else "PM"
                }
                if networkName(self.bot, server) not in self.tells:
                    self.tells[networkName(self.bot, server)] = []
                self.tells[networkName(self.bot, server)].append(message)
                sentTells.append(recep)
            if len(sentTells) > 0:
                if command == "tellafter":
                    m = "Okay, I'll tell {} that when they speak after {}.".format("&".join(sentTells),
                                                                                   strftimeWithTimezone(date))
                else:
                    m = "Okay, I'll tell {} that next time they speak.".format("&".join(sentTells))
                self.replyPRIVMSG(server, source, m)
            self.bot.storage["tells"] = self.tells
        elif command == "stells":
            if networkName(self.bot, server) not in self.tells:
                return
            tells = []
            for tell in self.tells[networkName(self.bot, server)]:
                if tell["from"].lower() == data["user"].nick.lower():
                    tells.append(self._parseSentTell(tell))
            if len(tells) > 0:
                for tell in tells:
                    self.replyNOTICE(server, data["user"].nick, tell)
            else:
                self.replyNOTICE(server, data["user"].nick, "No undelivered messages sent by you were found.")
        elif command == "rtell":
            if len(params) == 0:
                self.replyPRIVMSG(server, source, "Remove what?")
                return
            if networkName(self.bot, server) not in self.tells:
                self.replyNOTICE(server, data["user"].nick, "No tells matching \"{}\" were found.".format(params[0]))
                return
            tells = [x for x in self.tells[networkName(self.bot, server)] if x["from"].lower() == data[
                "user"].nick.lower()]
            for tell in tells:
                if re.search(" ".join(params), tell["body"], re.IGNORECASE):
                    self.tells[networkName(self.bot, server)].remove(tell)
                    self.bot.storage["tells"] = self.tells
                    m = "Message \"{}\" was removed from the message database.".format(self._parseSentTell(tell))
                    self.replyNOTICE(server, data["user"].nick, m)
                    break
            else:
                self.replyNOTICE(server, data["user"].nick, "No tells matching \"{}\" were found.".format(params[0]))

    def _processTells(self, server, source, nick):
        if networkName(self.bot, server) not in self.tells:
            return
        chanTells = []
        pmTells = []
        for tell in self.tells[networkName(self.bot, server)][:]:
            if not any(fnmatch(nick.lower(), r) for r in tell["to"].split("/")):
                continue
            if now() < tell["datetoreceive"]:
                continue
            if tell["source"][0] in self.bot.servers[server].supportHelper.chanTypes and len(chanTells) < 3:
                if tell["source"] == source:
                    chanTells.append(tell)
                    self.tells[networkName(self.bot, server)].remove(tell)
            elif tell["source"][0] not in self.bot.servers[server].supportHelper.chanTypes:
                pmTells.append(tell)
                self.tells[networkName(self.bot, server)].remove(tell)
        for tell in chanTells:
            self.replyPRIVMSG(server, source, self._parseTell(nick, tell))
        for tell in pmTells:
            self.replyPRIVMSG(server, nick, self._parseTell(nick, tell))
        if len(chanTells) > 0 or len(pmTells) > 0:
            self.bot.storage["tells"] = self.tells

    def _parseTell(self, nick, tell):
        return "{}: {} < From {} ({} ago).".format(nick, tell["body"], tell["from"], timeDeltaString(now(), tell["date"]))

    def _parseSentTell(self, tell):
        return "{} < Sent to {} on {}, to be received on {} in {}.".format(tell["body"], tell["to"],
                                                                           strftimeWithTimezone(tell["date"]),
                                                                           strftimeWithTimezone(tell["datetoreceive"]),
                                                                           tell["source"])


tellCommand = TellCommand()

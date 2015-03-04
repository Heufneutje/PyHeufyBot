from twisted.internet.task import LoopingCall
from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils import isNumber, networkName
from heufybot.utils.timeutils import now, strftimeWithTimezone, timeDeltaString
from zope.interface import implements
from datetime import datetime, timedelta
import re


class EventCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Event"

    def triggers(self):
        return ["event", "events", "timetill", "timesince", "dateof", "revent", "subevent", "unsubevent"]

    def load(self):
        self.help = "Commands: event <yyyy-MM-dd> (<HH:mm>) <event>, events (<days>), timetill <event>, timesince " \
                    "<event>, dateof <event>, revent <event>, subevent, unsubevent | Add, request or remove an event " \
                    "or subscribe to them."
        self.commandHelp = {
            "event": "event <yyyy-MM-dd> (<HH:mm>) <event> | Add an event to the events database.",
            "events": "events <days> | Request all events that occur within the given number of days. The default is "
                      "a week. The maximum is a year.",
            "timetill": "timetill <event> | Request the amount of time until a specified event occurs.",
            "timesince": "timesince <event> | Request the amount of time since a specified event occurred.",
            "dateof": "dateof <event> | Request the date of a specified event.",
            "revent": "revent <event> | Remove a specified event that was added by you from the events database.",
            "subevent": "subevent | Subscribe to event announcements. PM to subscribe to them in PM. Requires admin "
                        "permission to subscribe channels.",
            "unbsubevent": "unsubevent | Unsubscribe to event announcements. PM to unsubscribe from them in PM. "
                          "Requires admin permission to unsubscribe channels."
        }
        if "events" not in self.bot.storage:
            self.bot.storage["events"] = {}
        self.events = self.bot.storage["events"]
        if "event-subs" not in self.bot.storage:
            self.bot.storage["event-subs"] = {}
        self.subscriptions = self.bot.storage["event-subs"]
        self.announcementLoopCall = LoopingCall(self.checkEvents)
        self.announcementLoopCall.start(300, now=True) # Announce events every 5 minutes

    def checkPermissions(self, server, source, user, command):
        if command in ["subevent", "unsubevent"] and source[0] in self.bot.servers[server].supportHelper.chanTypes:
            channel = self.bot.servers[server].channels[source]
            if channel.userIsChanOp(user):
                return True
            return not self.bot.moduleHandler.runActionUntilFalse("checkadminpermission", server, source, user,
                                                                  "event-subscribe")
        return True

    def execute(self, server, source, command, params, data):
        if networkName(self.bot, server) not in self.events:
            self.events[networkName(self.bot, server)] = []
        if command == "event":
            if len(params) == 0:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Add what event?")
                return
            try:
                date = datetime.strptime(" ".join(params[0:2]), "%Y-%m-%d %H:%M")
                eventOffset = 2
                if len(params) < 3:
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Add what event?")
                    return
            except ValueError:
                try:
                    date = datetime.strptime(params[0], "%Y-%m-%d")
                    eventOffset = 1
                    if len(params) < 2:
                        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Add what event?")
                        return
                except ValueError:
                    e = "The date format you specified is invalid. The format is yyyy-MM-dd or yyyy-MM-dd HH:mm."
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, e)
                    return
            event = {
                "event": " ".join(params[eventOffset:]),
                "date": date,
                "user": data["user"].nick,
                "fired": True if date < now() else False
            }
            self.events[networkName(self.bot, server)].append(event)
            self.bot.storage["events"] = self.events
            m = "Event \"{}\" on date {} was added to the events database!".format(event["event"],
                                                                                   strftimeWithTimezone(date))
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
        elif command == "timetill":
            if len(params) == 0:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "You didn't specify an event")
                return
            events = [x for x in self.events[networkName(self.bot, server)] if x["date"] > now()]
            events.sort(key=lambda item:item["date"])
            for event in events:
                if re.search(" ".join(params), event["event"], re.IGNORECASE):
                    m = "{}'s event \"{}\" will occur in {}.".format(event["user"], event["event"], timeDeltaString(
                        event["date"], now()))
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
                    break
            else:
                m = "No events matching \"{}\" were found in the events database.".format(" ".join(params))
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
        elif command == "timesince":
            if len(params) == 0:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "You didn't specify an event")
                return
            events = [x for x in self.events[networkName(self.bot, server)] if x["date"] < now()]
            events.sort(key=lambda item:item["date"], reverse=True)
            for event in events:
                if re.search(" ".join(params), event["event"], re.IGNORECASE):
                    m = "{}'s event \"{}\" occurred {} ago.".format(event["user"], event["event"], timeDeltaString(
                        now(), event["date"]))
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
                    break
            else:
                m = "No events matching \"{}\" were found in the events database.".format(" ".join(params))
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
        elif command == "dateof":
            if len(params) == 0:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "You didn't specify an event")
                return
            events = [x for x in self.events[networkName(self.bot, server)] if x["date"] > now()]
            events.sort(key=lambda item:item["date"])
            for event in events:
                if re.search(" ".join(params), event["event"], re.IGNORECASE):
                    m = "{}'s event \"{}\" will occur on {}.".format(event["user"], event["event"],
                                                                  strftimeWithTimezone(event["date"]))
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
                    break
            else:
                events = [x for x in self.events[networkName(self.bot, server)] if x["date"] < now()]
                events.sort(key=lambda item:item["date"], reverse=True)
                for event in events:
                    if re.search(" ".join(params), event["event"], re.IGNORECASE):
                        m = "{}'s event \"{}\" occurred on {}.".format(event["user"], event["event"],
                                                                      strftimeWithTimezone(event["date"]))
                        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
                        break
                else:
                    m = "No events matching \"{}\" were found in the events database.".format(" ".join(params))
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
        elif command == "events":
            if len(params) == 0 or not isNumber(params[0]):
                days = 7
            else:
                days = int(params[0]) if int(params[0]) < 356 else 356
            events = [x["event"] for x in self.events[networkName(self.bot, server)] if x["date"] > now() and x[
                "date"] <= now() + timedelta(days)]
            dayString = "" if days == 1 else "s"
            if len(events) > 0:
                m = "Events occurring in the next {} day{}: {}.".format(days, dayString, ", ".join(events))
            else:
                m = "No events are occurring in the next {} day{}.".format(days, dayString)
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
        elif command == "revent":
            if len(params) == 0:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "You didn't specify an event")
                return
            events = [x for x in self.events[networkName(self.bot, server)] if x["date"] > now()]
            events.sort(key=lambda item:item["date"])
            for event in events:
                if re.search(" ".join(params), event["event"], re.IGNORECASE):
                    self.events[networkName(self.bot, server)].remove(event)
                    self.bot.storage["events"] = self.events
                    m = "{}'s event \"{}\" with date {} has been removed from the events database.".format(
                        event["user"], event["event"], strftimeWithTimezone(event["date"]))
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
                    break
            else:
                events = [x for x in self.events[networkName(self.bot, server)] if x["date"] < now() and x[
                    "user"].lower() == data["user"].nick.lower()]
                events.sort(key=lambda item:item["date"], reverse=True)
                for event in events:
                    if re.search(" ".join(params), event["event"], re.IGNORECASE):
                        self.events[networkName(self.bot, server)].remove(event)
                        self.bot.storage["events"] = self.events
                        m = "{}'s event \"{}\" with date {} has been removed from the events database.".format(
                            event["user"], event["event"], strftimeWithTimezone(event["date"]))
                        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
                        break
                else:
                    m = "No events matching \"{}\" by you were found in the events database.".format(" ".join(params))
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)
        elif command == "subevent" or command == "unsubevent":
            if networkName(self.bot, server) not in self.subscriptions:
                self.subscriptions[networkName(self.bot, server)] = []
            src = source if "channel" in data else data["user"].nick
            subAction = command == "subevent"
            self._handleSubscription(server, src, subAction)

    def checkEvents(self):
        for network in self.subscriptions:
            try:
                server = [x for x in self.bot.servers.itervalues() if x.supportHelper.network == network][0].name
            except IndexError: # We're not currently connected to this network
                continue
            sources = [x for x in self.subscriptions[network] if x in self.bot.servers[server].channels or x in
                       self.bot.servers[server].users]
            if len(sources) == 0:
                continue # Only fire events if there's a channel or user to fire them at
            events = []
            if network not in self.events:
                continue
            for i in range(0, len(self.events[network])):
                event = self.events[network][i]
                if event["date"] < now() and event["fired"] == False:
                    events.append(event)
                    self.events[network][i]["fired"] = True
            if len(events) == 0:
                continue
            self.bot.storage["events"] = self.events
            for source in sources:
                for event in events:
                    m = "{}'s event \"{}\" is happening right now!".format(event["user"], event["event"])
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)

    def _handleSubscription(self, server, source, subAction):
        if subAction:
            if source not in self.subscriptions[networkName(self.bot, server)]:
                self.subscriptions[networkName(self.bot, server)].append(source)
                self.bot.storage["event-subs"] = self.subscriptions
                m = "{} is now subscribed to event announcements.".format(source)
            else:
                m = "{} is already subscribed to event announcements!".format(source)
        else:
            if source in self.subscriptions[networkName(self.bot, server)]:
                self.subscriptions[networkName(self.bot, server)].remove(source)
                self.bot.storage["event-subs"] = self.subscriptions
                m = "{} is now unsubscribed from event announcements.".format(source)
            else:
                m = "{} is not subscribed to event announcements!".format(source)
        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, m)

eventCommand = EventCommand()

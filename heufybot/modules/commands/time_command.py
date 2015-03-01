from twisted.plugin import IPlugin
from heufybot.moduleinterface import IBotModule
from heufybot.modules.commandinterface import BotCommand
from heufybot.utils.timeutils import now, timestamp
from zope.interface import implements
from datetime import datetime


class TimeCommand(BotCommand):
    implements(IPlugin, IBotModule)

    name = "Time"
    timeBaseURL = "https://maps.googleapis.com/maps/api/timezone/json?"

    def triggers(self):
        return ["time"]

    def load(self):
        self.help = "Commands: time <lat> <lon>, time <place>, time <nickname> | Get the current local time for the " \
                    "given latlon, place or user."
        self.commandHelp = {}

    def execute(self, server, source, command, params, data):
        # Use the user's nickname as a parameter if none were given
        if len(params) == 0:
            params.append(data["user"].nick)
            selfSearch = True
        else:
            selfSearch = False

        # Try using latlon to get the location
        try:
            lat = float(params[0])
            lon = float(params[1])
            location = self.bot.moduleHandler.runActionUntilValue("geolocation-latlon", lat, lon)
            if not location:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I can't determine locations at the moment. "
                                                                          "Try again later.")
                return
            if not location["success"]:
                self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I don't think that's even a location in "
                                                                          "this multiverse...")
                return
            self._handleCommandWithLocation(server, source, location)
            return
        except (IndexError, ValueError):
            pass # The user did not give a latlon, so continue using other methods

        # Try to determine the user's location from a nickname
        if self.bot.config.serverItemWithDefault(server, "use_userlocation", False):
            userLoc = self.bot.moduleHandler.runActionUntilValue("userlocation", server, source, params[0], selfSearch)
            if selfSearch:
                if not userLoc:
                    return
                elif not userLoc["success"]:
                    return
            if userLoc and userLoc["success"]:
                if "lat" in userLoc:
                    location = self.bot.moduleHandler.runActionUntilValue("geolocation-latlon", userLoc["lat"],
                                                                          userLoc["lon"])
                else:
                    location = self.bot.moduleHandler.runActionUntilValue("geolocation-place", userLoc["place"])
                if not location:
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I can't determine locations at the "
                                                                              "moment. Try again later.")
                    return
                if not location["success"]:
                    self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I don't think that's even a location in "
                                                                              "this multiverse...")
                    return
                self._handleCommandWithLocation(server, source, location)
                return

        # Try to determine the location by the name of the place
        location = self.bot.moduleHandler.runActionUntilValue("geolocation-place", " ".join(params))
        if not location:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I can't determine locations at the moment. "
                                                                      "Try again later.")
            return
        if not location["success"]:
            self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "I don't think that's even a location "
                                                                      "in this multiverse...")
            return
        self._handleCommandWithLocation(server, source, location)

    def _handleCommandWithLocation(self, server, source, location):
        formattedTime = self._getTime(location["latitude"], location["longitude"])
        self.bot.servers[server].outputHandler.cmdPRIVMSG(source, "Location: {} | {}".format(location["locality"],
                                                                                             formattedTime))

    def _getTime(self, lat, lon):
        currentTime = timestamp(now())
        params = {
            "location": "{},{}".format(lat, lon),
            "timestamp": currentTime
        }
        result = self.bot.moduleHandler.runActionUntilValue("fetch-url", self.timeBaseURL, params)
        if not result:
            return "No time for this location could be found at this moment. Try again later."
        timeJSON = result.json()
        if timeJSON["status"] != "OK":
            if "error_message" in timeJSON:
                return timeJSON["error_message"]
            else:
                return "An unknown error occurred while requesting the time."
        resultDate = datetime.fromtimestamp(currentTime + int(timeJSON["dstOffset"]) + int(timeJSON["rawOffset"]))
        properDay = self._getProperDay(resultDate.day)
        formattedTime = resultDate.strftime("%H:%M (%I:%M %p) on %A, " + properDay + " of %B, %Y")
        return "Timezone: {} | Local time is {}".format(timeJSON["timeZoneName"], formattedTime)

    def _getProperDay(self, day):
        if day in [1, 21, 31]:
            return "{}st".format(day)
        elif day in [2, 22]:
            return "{}nd".format(day)
        elif day in [3, 33]:
            return "{}rd".format(day)
        else:
            return "{}th".format(day)

timeCommand = TimeCommand()
